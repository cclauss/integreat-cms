"""
This module contains utilities to repair or detect inconsistencies in a tree
"""
from __future__ import annotations
from django.db import transaction

import logging

from ..models import Page
from ..utils.tree_mutex import tree_mutex

logger = logging.getLogger(__name__)

class Printer:
    def __init__(self, print=None, error=None, success=None):
        self._print = print
        self._error = error
        self._success = success
        self._write = None
        self._bold = None

    @property
    def print(self):
        if not self._print:
            return logger.debug
        return self._print
    @print.setter
    def print(self, new):
        self._print = new

    @property
    def error(self):
        if not self._error:
            return self.print
        return self._error
    @error.setter
    def error(self, new):
        self._error = new

    @property
    def success(self):
        if not self._success:
            return self.print
        return self._success
    @success.setter
    def success(self, new):
        self._success = new

    @property
    def bold(self):
        if not self._bold:
            return lambda x: x
        return self._bold
    @bold.setter
    def bold(self, new):
        self._bold = new

    @property
    def write(self):
        if not self._write:
            return self.print
        return self._write
    @write.setter
    def write(self, new):
        self._write = new


@transaction.atomic
@tree_mutex('page')
def repair_tree(page_id: int = 0, commit: bool = False, printer: Printer = Printer()) -> None:
    pages_seen: list[int] = []
    if page_id:
        try:
            root_node = Page.objects.get(id=page_id)
        except Page.DoesNotExist as e:
            raise ValueError(
                f'The page with id "{page_id}" does not exist.'
            ) from e
        # Traversing to root node
        while root_node.parent:
            root_node = root_node.parent
        action = "Fixing" if commit else "Detecting problems in"
        printer.print(f"{action} tree with id {root_node.tree_id}...")
        calculate_left_right_values(root_node, 1, commit, pages_seen, printer)
        check_for_orphans(root_node.tree_id, pages_seen, printer)
    else:
        for root_node in Page.objects.filter(lft=1):
            action = "Fixing" if commit else "Detecting problems in"
            printer.print(f"{action} tree with id {root_node.tree_id}...")
            calculate_left_right_values(root_node, 1, commit, pages_seen, printer)
            check_for_orphans(root_node.tree_id, pages_seen, printer)

def check_tree_fields(tree_node: Page, left: int, right: int, printer: Printer = Printer()) -> bool:
    """
    Check whether the tree fields are correct

    :param tree_node: The current node
    :param left: The new left value of the node
    :param right: The new right value of the node
    :return: Whether the tree fields of the node are valid
    """
    valid = True
    printer.write(printer.bold(f"Page {tree_node.id}:"))
    printer.success(f"\tparent_id: {tree_node.parent_id}")
    if not tree_node.parent or tree_node.tree_id == tree_node.parent.tree_id:
        printer.success(f"\ttree_id: {tree_node.tree_id}")
    else:
        printer.error(
            f"\ttree_id: {tree_node.tree_id} → {tree_node.parent.tree_id}"
        )
        valid = False
    if tree_node.parent_id:
        if tree_node.depth == tree_node.parent.depth + 1:
            printer.success(f"\tdepth: {tree_node.depth}")
        else:
            printer.error(
                f"\tdepth: {tree_node.depth} → {tree_node.parent.depth + 1}"
            )
            valid = False
    elif tree_node.depth == 1:
        printer.success(f"\tdepth: {tree_node.depth}")
    else:
        printer.error(f"\tdepth: {tree_node.depth} → 1")
        valid = False
    if tree_node.lft == left:
        printer.success(f"\tlft: {tree_node.lft}")
    else:
        printer.error(f"\tlft: {tree_node.lft} → {left}")
        valid = False
    if tree_node.rgt == right:
        printer.success(f"\trgt: {tree_node.rgt}")
    else:
        printer.error(f"\trgt: {tree_node.rgt} → {right}")
        valid = False
    return valid

def check_for_orphans(tree_id: int, commit: bool = False, pages_seen: list[int] = [], printer: Printer = Printer()) -> None:
    """
    Check whether orphans exist (pages with the same tree_id, but its ancestors are in another tree)

    :param tree_id: The current tree id
    """
    if orphans := Page.objects.filter(tree_id=tree_id).exclude(
        id__in=pages_seen
    ):
        printer.error(
            "\n💣 Orphans detected! The following pages share the tree id "
            f"{tree_id} but don't have a relation to the root node:"
        )
        for orphan in orphans:
            printer.write(printer.bold(f"Page {orphan.id}:"))
            printer.error(f"\tparent_id: {orphan.parent_id}")
            if orphan.parent_id:
                printer.error(f"\tparent.tree_id: {orphan.parent.tree_id}")
            printer.write(
                printer.bold(
                    f"\tdepth {orphan.depth}\n"
                    f"\tlft: {orphan.lft}\n"
                    f"\trgt: {orphan.rgt}"
                )
            )
            if commit:
                repair_tree(orphan.pk, commit, printer=printer)

def calculate_left_right_values(
    tree_node: Page, left: int, commit: bool, pages_seen: list[int] = [], printer: Printer = Printer()
) -> int:
    """
    Recursively calculate the left and right value for a given node and its
    children.

    :param tree_node: A node of a MPTT tree
    :param left: The new left value of the node
    :param commit: Whether changes should be written to the database
    :return: The new right value of the node
    """
    right = left

    for child in tree_node.children.all():
        right = calculate_left_right_values(child, right + 1, commit, pages_seen, printer)

    right += 1

    valid = check_tree_fields(tree_node, left, right, printer)

    if not valid and commit:
        if tree_node.parent:
            tree_node.tree_id = tree_node.parent.tree_id
            tree_node.depth = tree_node.parent.depth + 1
        tree_node.rgt = right
        tree_node.lft = left
        tree_node.save()
        logger.info("Fixed tree fields of %r", tree_node)

    pages_seen.append(tree_node.id)

    return right


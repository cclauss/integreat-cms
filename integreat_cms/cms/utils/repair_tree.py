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
    """
    Select printer for stdout or log file
    """
    def __init__(self, print_func=None, error=None, success=None):
        self._print = print_func
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
@tree_mutex
def repair_tree(page_id: int = 0, commit: bool = False, printer: Printer = Printer(), fix_orphans: bool = True) -> None:
    pages_seen: list[int] = []
    orphans = set()

    mptt_fixer = MPTTFixer()

    if page_id:
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist as e:
            raise ValueError(
                f'The page with id "{page_id}" does not exist.'
            ) from e
        root_node = None
        for tree_node in mptt_fixer.get_fixed_tree_of_page(page.pk):
            # the first node is always the root node
            if root_node is None:
                root_node = tree_node
            action = "Fixing" if commit else "Detecting problems in"
            printer.print(f"{action} tree with id {root_node.tree_id}...")
            check_tree_fields(Page.objects.get(id=tree_node.pk), tree_node.lft, tree_node.rgt, printer)
        check_for_orphans(root_node.tree_id, pages_seen, printer)
    else:
        for root_node in Page.objects.filter(lft=1):
            action = "Fixing" if commit else "Detecting problems in"
            printer.print(f"{action} tree with id {root_node.tree_id}...")
            orphans.update(set(check_for_orphans(root_node.tree_id, pages_seen, printer)))

        if commit:
            for page in mptt_fixer.fixed_nodes:
                check_tree_fields(tree_node, left, right, printer)
                page.save()

def check_tree_fields(self, tree_node: Page, left: int, right: int, printer: Printer = Printer()) -> bool:
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

def check_for_orphans(tree_id: int, pages_seen: list[int] = [], printer: Printer = Printer()) -> None:
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
        return orphans
    return []

class MPTTFixer:
    """
    eats all nodes and coughs out fixed LFT, RGT and depth values. Uses the parent field
    to fix hierarchy and sorts siblings by (potentially inconsistent) lft.
    """

    def __init__(self):
        """
        Creates a fixed tree when initializing class but does not save results
        """
        self.broken_nodes = list(Page.objects.all().order_by('tree_id', 'lft'))
        # Dictionaries keep the insert order as of Python 3.7
        self.fixed_nodes = {}
        self.get_root_nodes()
        self.get_all_nodes()
        self.tree_counter = 0

    def get_root_nodes(self):
        """
        extract root nodes and reset lft + rgt values
        """
        tree_node_counter
        for node in self.broken_nodes:
            if node.parent is None:
                node.lft = 1
                node.rgt = 2
                node.depth = 1
                node.children = []
                self.fixed_nodes[node.pk] = node
                self.existing_nodes.remove(node)

    def get_all_nodes(self):
        """
        Get all remaining nodes, add add them to the new/fixed tree
        """
        for node in self.broken_nodes:
            parent = self.fixed_nodes[node.parent]
            node.children = []
            self.fixed_nodes[parent.pk].children.append(node.pk)
            node = self.calculate_lft_rgt(node, parent)

            # append fixed node to tree and update ancestors lft/rgt
            self.fixed_nodes[node.pk] = node
            self.update_ancestors_rgt(node)

    def calculate_lft_rgt(self, node: Page, parent: Page):
        """
        add a new node to the existing MPTT structure. As we sorted by lft, we always add
        to the right of existing nodes.
        """
        if not parent.children:
            # first child node, use lft of parent to calculate node lft/rgt
            node.lft = parent.lft + 1
            node.rgt = node.lft + 1
            node.depth = parent.depth + 1
        else:
            # parent has children. Get right-most sibling and continue lft from there.
            left_sibling_pk = next((pk for pk in self.fixed_nodes if pk == parent.children[-1]))
            node.lft = self.fixed_nodes[left_sibling_pk].rgt + 1
            node.rgt = node.lft + 1
            node.depth = self.fixed_nodes[left_sibling_pk].depth
        return node

    def update_ancestors_rgt(self, node: Page):
        """
        As we only append siblings to the right, we only need to modify the rgt values
        of all ancestors to adopt the new node into the tree.
        """
        parent = self.fixed_nodes[node.parent]
        self.fixed_nodes[parent.pk].rgt = node.rgt + 1
        node = self.fixed_nodes[parent.pk]
        while node.parent:
            self.fixed_nodes[parent.pk].rgt = node.rgt + 1
            node = parent

    def get_fixed_page_nodes(self):
        """
        Yield all page tree nodes
        """
        yield self.fixed_nodes.items()

    def get_fixed_tree_of_page(self, node_id: int):
        """
        get all nodes of page tree, either identfied by one page or the (new) tree ID.
        """
        tree_id = self.fixed_nodes[node_id].tree_id
        for node in self.fixed_nodes.items():
            if node.tree_id == tree_id:
                yield node
        yield

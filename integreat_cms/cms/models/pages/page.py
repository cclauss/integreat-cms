import logging

from html import escape

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from ...utils.translation_utils import ugettext_many_lazy as __
from ..abstract_content_model import ContentQuerySet
from ..abstract_tree_node import AbstractTreeNode, TreeNodeQuerySet, TreeNodeManager
from ..decorators import modify_fields
from .abstract_base_page import AbstractBasePage
from .page_translation import PageTranslation

logger = logging.getLogger(__name__)


class PageQuerySet(TreeNodeQuerySet, ContentQuerySet):
    """
    Custom queryset for pages to inherit methods from both querysets for tree nodes and content objects
    """


# pylint: disable=too-few-public-methods
class PageManager(TreeNodeManager):
    """
    Custom manager for pages to inherit methods from both managers for tree nodes and content objects
    """

    def get_queryset(self):
        """
        Sets the custom queryset as the default.

        :return: The sorted queryset
        :rtype: ~integreat_cms.cms.models.pages.page.PageQuerySet
        """
        return PageQuerySet(self.model).order_by("tree_id", "lft")


@modify_fields(parent={"verbose_name": _("parent page")})
class Page(AbstractTreeNode, AbstractBasePage):
    """
    Data model representing a page.
    """

    icon = models.ForeignKey(
        "cms.MediaFile",
        verbose_name=_("icon"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    mirrored_page = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="mirroring_pages",
        verbose_name=_("mirrored page"),
        help_text=_(
            "If the page embeds live content from another page, it is referenced here."
        ),
    )
    mirrored_page_first = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        verbose_name=_("Position of mirrored page"),
        help_text=_(
            "If a mirrored page is set, this field determines whether the live content is embedded before the content of this page or after."
        ),
    )
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="editable_pages",
        verbose_name=_("editors"),
        help_text=__(
            _("A list of users who have the permission to edit this specific page."),
            _(
                "Only has effect if these users do not have the permission to edit pages anyway."
            ),
        ),
    )
    publishers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="publishable_pages",
        verbose_name=_("publishers"),
        help_text=__(
            _("A list of users who have the permission to publish this specific page."),
            _(
                "Only has effect if these users do not have the permission to publish pages anyway."
            ),
        ),
    )
    organization = models.ForeignKey(
        "cms.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("responsible organization"),
        help_text=_(
            "This allows all members of the organization to edit and publish this page."
        ),
    )

    #: Custom model manager to inherit methods from tree manager as well as the custom content queryset
    objects = PageManager()

    @staticmethod
    def get_translation_model():
        """
        Returns the translation model of this content model

        :return: The class of translations
        :rtype: type
        """
        return PageTranslation

    @cached_property
    def explicitly_archived_ancestors(self):
        """
        This returns all of the page's ancestors which are archived.

        :return: The QuerySet of archived ancestors
        :rtype: ~treebeard.ns_tree.NS_NodeQuerySet [ ~integreat_cms.cms.models.pages.page.Page ]
        """
        return [
            ancestor
            for ancestor in self.get_cached_ancestors()
            if ancestor.explicitly_archived
        ]

    @cached_property
    def implicitly_archived(self):
        """
        This checks whether one of the page's ancestors is archived which means that this page is implicitly archived as well.

        :return: Whether or not this page is implicitly archived
        :rtype: bool
        """
        return self.explicitly_archived_ancestors

    @cached_property
    def archived(self):
        """
        A hierarchical page is archived either explicitly if ``explicitly_archived=True`` or implicitly if one of its
        ancestors is explicitly archived.

        :return: Whether or not this page is archived
        :rtype: bool
        """
        return self.explicitly_archived or self.implicitly_archived

    @classmethod
    def get_root_pages(cls, region_slug):
        """
        Gets all root pages

        :param region_slug: Slug defining the region
        :type region_slug: str

        :return: All root pages i.e. pages without parents
        :rtype: ~treebeard.ns_tree.NS_NodeQuerySet [ ~integreat_cms.cms.models.pages.page.Page ]
        """
        return cls.get_region_root_nodes(region_slug=region_slug)

    def get_mirrored_page_translation(self, language_slug):
        """
        Mirrored content always includes the live content from another page. This content needs to be added when
        delivering content to end users.

        :param language_slug: The slug of the requested :class:`~integreat_cms.cms.models.languages.language.Language`
        :type language_slug: str

        :return: The content of a mirrored page
        :rtype: str
        """
        if self.mirrored_page:
            return self.mirrored_page.get_public_translation(language_slug)
        return None

    def __str__(self):
        """
        This overwrites the default Django :meth:`~django.db.models.Model.__str__` method which would return ``Page object (id)``.
        It is used in the Django admin backend and as label for ModelChoiceFields.

        :return: A readable string representation of the page
        :rtype: str
        """
        label = " &rarr; ".join(
            [
                # escape page title because string is marked as safe afterwards
                escape(ancestor.best_translation.title)
                for ancestor in self.get_cached_ancestors(include_self=True)
            ]
        )
        # Add warning if page is archived
        if self.archived:
            label += " (&#9888; " + _("Archived") + ")"
        # mark as safe so that the arrow and the warning triangle are not escaped
        return mark_safe(label)

    class Meta:
        #: The verbose name of the model
        verbose_name = _("page")
        #: The plural verbose name of the model
        verbose_name_plural = _("pages")
        #: The name that will be used by default for the relation from a related object back to this one
        default_related_name = "pages"
        #: The default permissions for this model
        default_permissions = ("change", "delete", "view")
        #: The custom permissions for this model
        permissions = (
            ("publish_page", "Can publish page"),
            ("grant_page_permissions", "Can grant page permission"),
        )

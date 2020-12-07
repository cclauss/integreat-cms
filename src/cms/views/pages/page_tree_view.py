from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _, ugettext_lazy

from django.views.generic import TemplateView

from ...decorators import region_permission_required
from ...models import Region, Language


@method_decorator(login_required, name="dispatch")
@method_decorator(region_permission_required, name="dispatch")
class PageTreeView(PermissionRequiredMixin, TemplateView):
    """
    View for showing the page tree
    """

    #: Required permission of this view (see :class:`~django.contrib.auth.mixins.PermissionRequiredMixin`)
    permission_required = "cms.view_pages"
    #: Whether or not an exception should be raised if the user is not logged in (see :class:`~django.contrib.auth.mixins.LoginRequiredMixin`)
    raise_exception = True
    #: Template for list of non-archived pages
    template = "pages/page_tree.html"
    #: Template for list of archived pages
    template_archived = "pages/page_tree_archived.html"
    #: Whether or not to show archived pages
    archived = False
    #: Messages in confirmation dialogs for delete, archive, restore operations
    confirmation_dialog_context = {
        "archive_dialog_title": ugettext_lazy(
            "Please confirm that you really want to archive this page"
        ),
        "archive_dialog_text": ugettext_lazy(
            "All translations of this page will also be archived."
        ),
        "restore_dialog_title": ugettext_lazy(
            "Please confirm that you really want to restore this page"
        ),
        "restore_dialog_text": ugettext_lazy(
            "All translations of this page will also be restored."
        ),
        "delete_dialog_title": ugettext_lazy(
            "Please confirm that you really want to delete this page"
        ),
        "delete_dialog_text": ugettext_lazy(
            "All translations of this page will also be deleted."
        ),
    }

    @property
    def template_name(self):
        """
        Select correct HTML template, depending on :attr:`~cms.views.pages.page_tree_view.PageTreeView.archived` flag
        (see :class:`~django.views.generic.base.TemplateResponseMixin`)

        :return: Path to HTML template
        :rtype: str
        """

        return self.template_archived if self.archived else self.template

    def get(self, request, *args, **kwargs):
        """
        Render page tree

        :param request: The current request
        :type request: ~django.http.HttpResponse

        :param args: The supplied arguments
        :type args: list

        :param kwargs: The supplied keyword arguments
        :type kwargs: dict

        :return: The rendered template response
        :rtype: ~django.template.response.TemplateResponse
        """

        # current region
        region_slug = kwargs.get("region_slug")
        region = Region.get_current_region(request)

        # current language
        language_code = kwargs.get("language_code")
        if language_code:
            language = Language.objects.get(code=language_code)
        elif region.default_language:
            return redirect(
                "pages",
                **{
                    "region_slug": region_slug,
                    "language_code": region.default_language.code,
                }
            )
        else:
            messages.error(
                request,
                _("Please create at least one language node before creating pages."),
            )
            return redirect(
                "language_tree",
                **{
                    "region_slug": region_slug,
                }
            )

        if not request.user.has_perm("cms.edit_page"):
            messages.warning(
                request, _("You don't have the permission to edit or create pages.")
            )

        return render(
            request,
            self.template_name,
            {
                **self.confirmation_dialog_context,
                "current_menu_item": "pages",
                "pages": region.pages.filter(archived=self.archived),
                "archived_count": region.pages.filter(archived=True).count(),
                "language": language,
                "languages": region.languages,
            },
        )

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from integreat_cms.cms.views.translate_pages.translate_pages_context_mixin import TranslatePagesContextMixin

from ...decorators import permission_required

# @TODO: perm for machine translation
@method_decorator(permission_required("cms.view_page"), name="dispatch")
class PartialTranslatePagesTreeView(TemplateView, TranslatePagesContextMixin):
    """
    View for rendering a partial page tree
    """

    #: Template for a partial page tree
    template = "translate_pages/_translate_pages_tree_children.html"

    # pylint: disable=unused-argument
    def get(self, request, *args, **kwargs):
        r"""
        Retrieve the rendered subtree of a given root page

        :param request: The current request
        :type request: ~django.http.HttpRequest

        :param \*args: The supplied arguments
        :type \*args: list

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict

        :return: The rendered template response
        :rtype: ~django.template.response.TemplateResponse
        """
        tree_id = int(kwargs.get("tree_id"))
        region = request.region
        language = region.get_language_or_404(
            kwargs.get("language_slug"), only_active=True
        )
        # Get the tree of the given id
        pages = (
            region.pages.filter(tree_id=tree_id)
            .prefetch_major_translations()
            .prefetch_related("mirroring_pages")
            .cache_tree(archived=False)
        )
        # The first element must be the root node
        parent = pages[0]
        # The remaining pages are the descendants
        children = pages[1:]
        return render(
            request,
            self.template,
            {
                **self.get_context_data(**kwargs),
                "pages": children,
                "language": language,
                "languages": region.active_languages,
                "parent_id": parent.id,
            },
        )

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from ...decorators import staff_required
from ...models import Organization


@method_decorator(login_required, name="dispatch")
@method_decorator(staff_required, name="dispatch")
class OrganizationListView(PermissionRequiredMixin, TemplateView):
    """
    View for listing organizations
    """

    #: Required permission of this view (see :class:`~django.contrib.auth.mixins.PermissionRequiredMixin`)
    permission_required = "cms.manage_organizations"
    #: Whether or not an exception should be raised if the user is not logged in (see :class:`~django.contrib.auth.mixins.LoginRequiredMixin`)
    raise_exception = True
    #: The template to render (see :class:`~django.views.generic.base.TemplateResponseMixin`)
    template_name = "organizations/organization_list.html"
    #: The context dict passed to the template (see :class:`~django.views.generic.base.ContextMixin`)
    base_context = {"current_menu_item": "organizations"}

    def get(self, request, *args, **kwargs):
        """
        Render organization list

        :param request: The current request
        :type request: ~django.http.HttpResponse

        :param args: The supplied arguments
        :type args: list

        :param kwargs: The supplied keyword arguments
        :type kwargs: dict

        :return: The rendered template response
        :rtype: ~django.template.response.TemplateResponse
        """
        return render(
            request,
            self.template_name,
            {**self.base_context, "organizations": Organization.objects.all()},
        )
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from ...decorators import staff_required
from ...models import (
    PageFeedback,
    EventFeedback,
    EventListFeedback,
    OfferFeedback,
    OfferListFeedback,
    SearchResultFeedback,
    ImprintPageFeedback,
    RegionFeedback,
    Feedback,
)


@method_decorator(login_required, name="dispatch")
@method_decorator(staff_required, name="dispatch")
class AdminFeedbackListView(TemplateView):
    """
    View to list all admin feedback (technical feedback)
    """

    #: The template to render (see :class:`~django.views.generic.base.TemplateResponseMixin`)
    template_name = "feedback/admin_feedback_list.html"

    def get(self, request, *args, **kwargs):
        """
        Render admin feedback list

        :param request: Object representing the user call
        :type request: ~django.http.HttpRequest

        :param args: The supplied arguments
        :type args: list

        :param kwargs: The supplied keyword arguments
        :type kwargs: dict

        :return: The rendered template response
        :rtype: ~django.template.response.TemplateResponse
        """

        page_feedback = PageFeedback.objects.filter(is_technical=True)
        event_feedback = EventFeedback.objects.filter(is_technical=True)
        event_list_feedback = EventListFeedback.objects.filter(is_technical=True)
        offer_feedback = OfferFeedback.objects.filter(is_technical=True)
        offer_list_feedback = OfferListFeedback.objects.filter(is_technical=True)
        search_result_feedback = SearchResultFeedback.objects.filter(is_technical=True)
        imprint_page_feedback = ImprintPageFeedback.objects.filter(is_technical=True)
        region_feedback = RegionFeedback.objects.filter(is_technical=True)
        admin_feedback_exists = Feedback.objects.filter(is_technical=True).exists()

        return render(
            request,
            self.template_name,
            {
                "current_menu_item": "admin_feedback",
                "page_feedback": page_feedback,
                "event_feedback": event_feedback,
                "event_list_feedback": event_list_feedback,
                "offer_feedback": offer_feedback,
                "offer_list_feedback": offer_list_feedback,
                "search_result_feedback": search_result_feedback,
                "imprint_page_feedback": imprint_page_feedback,
                "region_feedback": region_feedback,
                "admin_feedback_exists": admin_feedback_exists,
            },
        )
"""
This module contains view actions for objects related to POIs.
"""
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from ...decorators import region_permission_required, staff_required
from ...models import POI

logger = logging.getLogger(__name__)


@login_required
@region_permission_required
@permission_required("cms.manage_pois", raise_exception=True)
def archive_poi(request, poi_id, region_slug, language_code):
    """
    Archive POI object

    :param request: The current request
    :type request: ~django.http.HttpResponse

    :param poi_id: The id of the POI which should be archived
    :type poi_id: int

    :param region_slug: The slug of the current region
    :type region_slug: str

    :param language_code: The code of the current language
    :type language_code: str

    :return: A redirection to the :class:`~cms.views.pois.poi_list_view.POIListView`
    :rtype: ~django.http.HttpResponseRedirect
    """
    poi = POI.objects.get(id=poi_id)

    poi.archived = True
    poi.save()

    messages.success(request, _("Location was successfully archived"))

    return redirect(
        "pois",
        **{
            "region_slug": region_slug,
            "language_code": language_code,
        }
    )


@login_required
@region_permission_required
@permission_required("cms.manage_pois", raise_exception=True)
def restore_poi(request, poi_id, region_slug, language_code):
    """
    Restore POI object (set ``archived=False``)

    :param request: The current request
    :type request: ~django.http.HttpResponse

    :param poi_id: The id of the POI which should be restored
    :type poi_id: int

    :param region_slug: The slug of the current region
    :type region_slug: str

    :param language_code: The code of the current language
    :type language_code: str

    :return: A redirection to the :class:`~cms.views.pois.poi_list_view.POIListView`
    :rtype: ~django.http.HttpResponseRedirect
    """
    poi = POI.objects.get(id=poi_id)

    poi.archived = False
    poi.save()

    messages.success(request, _("Location was successfully restored"))

    return redirect(
        "pois",
        **{
            "region_slug": region_slug,
            "language_code": language_code,
        }
    )


@login_required
@staff_required
def delete_poi(request, poi_id, region_slug, language_code):
    """
    Delete POI object

    :param request: The current request
    :type request: ~django.http.HttpResponse

    :param poi_id: The id of the POI which should be deleted
    :type poi_id: int

    :param region_slug: The slug of the current region
    :type region_slug: str

    :param language_code: The code of the current language
    :type language_code: str

    :return: A redirection to the :class:`~cms.views.pois.poi_list_view.POIListView`
    :rtype: ~django.http.HttpResponseRedirect
    """

    poi = POI.objects.get(id=poi_id)
    poi.delete()
    messages.success(request, _("Location was successfully deleted"))

    return redirect(
        "pois",
        **{
            "region_slug": region_slug,
            "language_code": language_code,
        }
    )


@login_required
@region_permission_required
@permission_required("cms.manage_pois", raise_exception=True)
# pylint: disable=unused-argument
def view_poi(request, poi_id, region_slug, language_code):
    """
    View POI object

    :param request: The current request
    :type request: ~django.http.HttpResponse

    :param poi_id: The id of the POI which should be viewed
    :type poi_id: int

    :param region_slug: The slug of the current region
    :type region_slug: str

    :param language_code: The code of the current language
    :type language_code: str

    :raises ~django.http.Http404: If user no translation exists for the requested POI and language

    :return: A redirection to the :class:`~cms.views.pois.poi_list_view.POIListView`
    :rtype: ~django.http.HttpResponseRedirect
    """
    #: The template to render (see :class:`~django.views.generic.base.TemplateResponseMixin`)
    template_name = "pois/poi_view.html"
    poi = POI.objects.get(id=poi_id)

    poi_translation = poi.get_translation(language_code)

    if not poi_translation:
        raise Http404

    return render(request, template_name, {"poi_translation": poi_translation})
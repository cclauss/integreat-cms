"""
This module contains views for generating the sitemap dynamically.
The views are class-based patches of the inbuilt views :func:`~django.contrib.sitemaps.views.index` and
:func:`~django.contrib.sitemaps.views.sitemap` of the :mod:`django.contrib.sitemaps` :doc:`django:ref/contrib/sitemaps`.
"""
import logging

from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.http import http_date
from django.views.generic.base import TemplateResponseMixin, View


from backend.settings import WEBAPP_URL
from cms.constants import region_status
from cms.models import Region

from .utils import get_sitemaps

logger = logging.getLogger(__name__)


class SitemapIndexView(TemplateResponseMixin, View):
    """
    This view allows to generate a sitemap index dynamically.
    It is a patched version of :func:`django.contrib.sitemaps.views.index` with the following changes:

    * Sitemaps dynamically queried on each request, not on the application startup
    * :attr:`~backend.settings.WEBAPP_URL` is used for the domain instead of the host of the sitemap
    * Empty sitemaps are not included in the index
    """

    #: The template to render (see :class:`~django.views.generic.base.TemplateResponseMixin`)
    template_name = "sitemap_index.xml"
    #: The content type to use for the response (see :class:`~django.views.generic.base.TemplateResponseMixin`)
    content_type = "application/xml"

    def get(self, request, *args, **kwargs):
        """
        This function handles a get request

        :param request: The current request
        :type request: ~django.http.HttpRequest

        :param args: The supplied args
        :type args: list

        :param kwargs: The supplied keyword args
        :type kwargs: dict

        :return: The rendered template response
        :rtype: ~django.template.response.TemplateResponse
        """

        logger.debug("Sitemap index requested with args %s and kwargs %s", args, kwargs)

        sitemaps = []
        # Only add active regions to the sitemap index
        for region in Region.objects.filter(status=region_status.ACTIVE):
            # Only add active languages to the sitemap index
            for language_tree_node in region.language_tree_nodes.filter(active=True):
                # Only add sitemaps with actual content (empty list evaluates to False)
                if get_sitemaps(region, language_tree_node.language):
                    sitemap_url = reverse(
                        "sitemap",
                        kwargs={
                            "region_slug": region.slug,
                            "language_code": language_tree_node.code,
                        },
                    )
                    absolute_url = f"{WEBAPP_URL}{sitemap_url}"
                    sitemaps.append(absolute_url)

        logger.debug("Sitemap index: %s", sitemaps)

        return self.render_to_response({"sitemaps": sitemaps})


class SitemapView(TemplateResponseMixin, View):
    """
    This view allows to generate a sitemap dynamically.
    A sitemap contains the urls of multiple :class:`~sitemap.sitemaps.WebappSitemap` instances, one for each content type.
    It is a patched version of :func:`django.contrib.sitemaps.views.sitemap` with the following changes:

    * Sitemaps dynamically queried on each request, not on the application startup
    * HTTP 404 returned if sitemap is empty
    * Support for pagination was dropped (only needed with more than 50000 urls per region and language)
    """

    #: The template to render (see :class:`~django.views.generic.base.TemplateResponseMixin`)
    template_name = "sitemap.xml"
    #: The content type to use for the response (see :class:`~django.views.generic.base.TemplateResponseMixin`)
    content_type = "application/xml"

    def get(self, request, *args, **kwargs):
        """
        This function handles a get request

        :param request: The current request
        :type request: ~django.http.HttpRequest

        :param args: The supplied args
        :type args: list

        :param kwargs: The supplied keyword args (should contain ``region_slug`` and ``language_code``)
        :type kwargs: dict

        :raises ~django.http.Http404: Raises a HTTP 404 if the either the region or language does not exist or is invalid
                                      or if the sitemap is empty.

        :return: The rendered template response
        :rtype: ~django.template.response.TemplateResponse
        """

        logger.debug("Sitemap requested with args %s and kwargs %s", args, kwargs)

        # Only return a sitemap if the region is active
        region = get_object_or_404(
            Region, slug=kwargs.get("region_slug"), status=region_status.ACTIVE
        )
        # Only return a sitemap if the language is active
        language = get_object_or_404(
            region.language_tree_nodes,
            language__code=kwargs.get("language_code"),
            active=True,
        ).language

        sitemaps = get_sitemaps(region, language)

        # Only return a sitemap if it contains any elements
        if not sitemaps:
            raise Http404

        # Join the lists of all urls of all sitemaps
        urls = sum(
            [sitemap.get_urls(site=get_current_site(request)) for sitemap in sitemaps],
            [],
        )
        # Pick the latest last_modified if all sitemaps
        last_modified = max([sitemap.latest_lastmod for sitemap in sitemaps])

        logger.debug("Sitemap urls %s", urls)

        response = self.render_to_response({"urlset": urls})
        response["Last-Modified"] = http_date(last_modified.timestamp())
        return response

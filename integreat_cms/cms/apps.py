import logging

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class CmsConfig(AppConfig):
    """
    This class represents the Django-configuration of the backend.

    See :class:`django.apps.AppConfig` for more information.

    :param name: The name of the app
    :type name: str
    """

    #: Full Python path to the application
    name = "integreat_cms.cms"
    #: Human-readable name for the application
    verbose_name = _("CMS")

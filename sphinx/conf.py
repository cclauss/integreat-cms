"""
Configuration file for the Sphinx documentation builder.

This file only contains the options which deviate from the default values.
For a full list see the documentation: :doc:`sphinx:usage/configuration`
"""

# -- Path setup --------------------------------------------------------------

import os
import sys
import inspect
import importlib

from datetime import date

from django import VERSION as django_version

from integreat_cms.core import settings


# Append project source directory to path environment variable
sys.path.append(os.path.abspath(".."))
# Append sphinx source directory to path environment variable to allow documentation for this file
sys.path.append(os.path.abspath("."))
#: The path to the django settings module (see :doc:`sphinxcontrib-django2:readme`)
django_settings = "integreat_cms.core.sphinx_settings"
#: The "major.minor" version of Django
django_version = f"{django_version[0]}.{django_version[1]}"

# -- Project information -----------------------------------------------------

#: The project name
project = "integreat-cms"
# pylint: disable=redefined-builtin
#: The copyright notice
copyright = f"{date.today().year} {settings.COMPANY}"
#: The project author
author = settings.COMPANY
#: GitHub username
github_username = "digitalfabrik"
#: GitHub repository name
github_repository = "integreat-cms"
#: GitHub URL
github_url = f"https://github.com/{github_username}/{github_repository}"
#: GitHub pages URL (target of gh-pages branch)
github_pages_url = f"https://{github_username}.github.io/{github_repository}"
# GitHub URL of Django repository
django_github_url = f"https://github.com/django/django/blob/stable/{django_version}.x"

#: The full version, including alpha/beta/rc tags
release = "2022.8.3"

# -- General configuration ---------------------------------------------------

#: All enabled sphinx extensions (see :ref:`sphinx-extensions`)
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",
    "sphinxcontrib_django2",
    "sphinx_rtd_theme",
    "sphinx_last_updated_by_git",
]
#: Enable cross-references to other documentations
intersphinx_mapping = {
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
    "geopy": ("https://geopy.readthedocs.io/en/stable/", None),
    "python": (
        f"https://docs.python.org/{sys.version_info.major}.{sys.version_info.minor}/",
        None,
    ),
    "pipenv": ("https://pipenv.pypa.io/en/latest/", None),
    "pytest": ("https://docs.pytest.org/en/latest/", None),
    "pytest-cov": ("https://pytest-cov.readthedocs.io/en/latest/", None),
    "pytest-django": ("https://pytest-django.readthedocs.io/en/latest/", None),
    "pytest-xdist": ("https://pytest-xdist.readthedocs.io/en/latest/", None),
    # "requests": ("https://docs.python-requests.org/en/master/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    "sphinx-rtd-theme": (
        "https://sphinx-rtd-theme.readthedocs.io/en/latest/",
        None,
    ),
    "sphinxcontrib-django2": (
        "https://sphinxcontrib-django2.readthedocs.io/en/latest/",
        None,
    ),
    "sphinx-rtd-tutorial": (
        "https://sphinx-rtd-tutorial.readthedocs.io/en/latest/",
        None,
    ),
    "django": (
        f"https://docs.djangoproject.com/en/{django_version}/",
        f"https://docs.djangoproject.com/en/{django_version}/_objects/",
    ),
    "django-debug-toolbar": (
        "https://django-debug-toolbar.readthedocs.io/en/latest/",
        None,
    ),
    "django-polymorphic": (
        "https://django-polymorphic.readthedocs.io/en/latest/",
        None,
    ),
    "django-treebeard": ("https://django-treebeard.readthedocs.io/en/latest/", None),
    "setuptools": ("https://setuptools.pypa.io/en/latest/", None),
    "twine": ("https://twine.readthedocs.io/en/latest/", None),
    "wsgi": ("https://wsgi.readthedocs.io/en/latest/", None),
    "weasyprint": ("https://doc.courtbouillon.org/weasyprint/stable/", None),
}
intersphinx_timeout = 5
#: The path for patched template files
templates_path = ["templates"]
#: Markup to shorten external links (see :doc:`sphinx:usage/extensions/extlinks`)
extlinks = {
    "github": (f"{github_url}/%s", None),
    "github-source": (f"{github_url}/blob/develop/%s", None),
    "django-source": (f"{django_github_url}/%s", None),
}
#: A string of reStructuredText that will be included at the end of every source file that is read. Used for substitutions.
rst_epilog = f"""
.. |github-username| replace:: {github_username}
.. |github-repository| replace:: {github_repository}
.. |github-pages-url| replace:: {github_pages_url}
"""
#: Warn about all references where the target cannot be found
nitpicky = True
#: A list of (type, target) tuples that should be ignored when :attr:`nitpicky` is ``True``
nitpick_ignore = [
    ("py:class", "_io.StringIO"),
    ("py:class", "builtins.int"),
    ("py:class", "builtins.AssertionError"),
    ("py:class", "builtins.int"),
    ("py:class", "NoneType"),
    ("py:class", "django.contrib.admin.helpers.ActionForm"),
    ("py:class", "django.contrib.admin.checks.ModelAdminChecks"),
    ("py:attr", "django.contrib.auth.models.Permission.user_set"),
    ("py:attr", "django.contrib.auth.models.Group.role"),
    ("py:attr", "django.contrib.auth.models.Group.user_set"),
    ("py:class", "django.contrib.auth.base_user.BaseUserManager"),
    ("py:class", "django.contrib.auth.hashers.BCryptSHA256PasswordHasher"),
    ("py:class", "django.utils.datastructures.MultiValueDict"),
    ("py:class", "django.contrib.auth.tokens.PasswordResetTokenGenerator"),
    ("py:func", "django.contrib.sitemaps.Sitemap._urls"),
    (
        "py:attr",
        "django.contrib.contenttypes.models.ContentType.polymorphic_cms.feedback_set+",
    ),
    ("py:class", "django.core.handlers.WSGIHandler"),
    ("py:class", "django.core.mail.EmailMultiAlternatives"),
    ("py:class", "django.core.serializers.base.ProgressBar"),
    ("py:class", "django.core.serializers.base.DeserializedObject"),
    ("py:class", "django.core.serializers.base.DeserializationError"),
    ("py:class", "django.core.serializers.base.SerializationError"),
    ("py:class", "django.core.serializers.xml_serializer.Serializer"),
    ("py:class", "django.core.serializers.xml_serializer.Deserializer"),
    ("py:class", "django.forms.models.ModelChoiceIterator"),
    ("py:class", "django.forms.widgets.LanguageTreeNodeForm"),
    ("py:class", "django.forms.widgets.PageForm"),
    ("py:func", "django.utils.text.capfirst"),
    ("py:class", "django.utils.xmlutils.SimplerXMLGenerator"),
    ("py:class", "linkcheck.apps.LinkcheckConfig"),
    ("py:class", "linkcheck.Linklist"),
    ("py:class", "linkcheck.models.Link"),
    ("py:attr", "linkcheck.models.Link.+"),
    ("py:attr", "linkcheck.models.Link.event_translations"),
    ("py:attr", "linkcheck.models.Link.event_translation"),
    ("py:attr", "linkcheck.models.Link.imprint_translation"),
    ("py:attr", "linkcheck.models.Link.page_translations"),
    ("py:attr", "linkcheck.models.Link.page_translation"),
    ("py:attr", "linkcheck.models.Link.poi_translations"),
    ("py:attr", "linkcheck.models.Link.poi_translation"),
    ("py:class", "polymorphic.query.PolymorphicQuerySet"),
    ("py:class", "PolymorphicQuerySet"),
    ("py:mod", "requests"),
    ("py:class", "requests.Response"),
    ("py:class", "webauthn.WebAuthnUser"),
    ("py:class", "xml.dom.minidom.Element"),
]
#: A list of prefixes that are ignored for sorting the Python module index
modindex_common_prefix = ["integreat_cms"]

# -- Options for HTML output -------------------------------------------------

#: The theme to use for HTML and HTML Help pages.
html_theme = "sphinx_rtd_theme"
#: Do not show the project name, only the logo
html_theme_options = {
    "logo_only": False,
    "collapse_navigation": False,
}
#: The logo shown in the menu bar
html_logo = "../integreat_cms/static/src/logos/integreat/integreat-logo-white.svg"
#: The favicon of the html doc files
html_favicon = "../integreat_cms/static/src/logos/integreat/integreat-icon.svg"
#: The url where the docs should be published (via gh-pages)
html_baseurl = github_pages_url
#: Do not include links to the documentation source (.rst files) in build
html_show_sourcelink = False
#: Do not include a link to sphinx
html_show_sphinx = False
#: Include last updated timestamp
html_last_updated_fmt = "%b %d, %Y"

# -- Source Code links to GitHub ---------------------------------------------


def linkcode_resolve(domain, info):
    """
    This function adds source code links to all modules (see :mod:`sphinx:sphinx.ext.linkcode`).
    It links all classes and functions to their source files on GitHub including line numbers.

    :param domain: The programming language of the given object (e.g. ``py``, ``c``, ``cpp`` or ``javascript``)
    :type domain: str

    :param info: Information about the given object. For a python object, it has the keys ``module`` and ``fullname``.
    :type info: dict

    :return: The URL of the given module on GitHub
    :rtype: str
    """
    module_str = info["module"]
    if domain != "py" or not module_str:
        return None
    item = importlib.import_module(module_str)
    line_number_reference = ""
    for piece in info["fullname"].split("."):
        item = getattr(item, piece)
        try:
            line_number_reference = f"#L{inspect.getsourcelines(item)[1]}"
            module_str = item.__module__
        except (TypeError, IOError):
            pass
    module = importlib.import_module(module_str)
    module_path = module_str.replace(".", "/")
    filename = module.__file__.partition(module_path)[2]
    if module_str.startswith("django."):
        url = django_github_url
    else:
        url = f"{github_url}/blob/develop"
    return f"{url}/{module_path}{filename}{line_number_reference}"


# -- Custom patches for autodoc ----------------------------------------------


# pylint: disable=unused-argument
def patch_django_for_autodoc(app):
    """
    Monkeypatch the docstring of ``get_sorted_pos_queryset()`` because the indentation levels are incorrect

    :param app: The Sphinx application object
    :type app: ~sphinx.application.Sphinx
    """
    # pylint: disable=import-outside-toplevel
    from treebeard.models import Node

    Node.get_sorted_pos_queryset.__doc__ = """
    :returns:

        A queryset of the nodes that must be moved to the right.
        Called only for Node models with :attr:`node_order_by`

    This function is based on _insertion_target_filters from django-mptt
    (BSD licensed) by Jonathan Buchanan:
    https://github.com/django-mptt/django-mptt/blob/0.3.0/mptt/signals.py
    """


def setup(app):
    """
    Connect to the ``django-configured`` event of :mod:`sphinxcontrib_django2` to monkeypatch application.

    :param app: The Sphinx application object
    :type app: ~sphinx.application.Sphinx
    """
    # Setup Django after config is initialized
    app.connect("django-configured", patch_django_for_autodoc)
    # Add crossref type for links to the pytest documentation
    app.add_crossref_type(
        directivename="fixture",
        rolename="fixture",
        indextemplate="pair: %s; fixture",
    )

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.test.client import Client
from django.urls import reverse

from integreat_cms.cms.constants import status
from integreat_cms.cms.constants.roles import EDITOR
from integreat_cms.cms.models.pages.page import Page
from integreat_cms.cms.models.regions.region import Region
from integreat_cms.cms.views.utils.hix import normalize_text
from tests.textlab_api.textlab_config import TEXTLAB_NORMALIZE_TEXT

if TYPE_CHECKING:
    from django.test.client import Client
    from pytest_django.fixtures import SettingsWrapper
    from pytest_httpserver.httpserver import HTTPServer


@pytest.mark.parametrize("input,output", TEXTLAB_NORMALIZE_TEXT)
def test_normalize_text(
    input: str,
    output: str,
) -> None:
    """
    Test for the text normalization function that is applied before sending text to the TextLab API
    """
    assert output == normalize_text(input)


@pytest.mark.django_db
@pytest.mark.parametrize("login_role_user", [EDITOR], indirect=True)
def test_hix_score_update(
    load_test_data: None,
    login_role_user: tuple[Client, str],
    settings: SettingsWrapper,
    httpserver: HTTPServer,
) -> None:
    """
    Check that the HIX score is requested and saved when the page translation is updated

    :param load_test_data: The fixture providing the test data (see :meth:`~tests.conftest.load_test_data`)
    :param login_role_user: The fixture providing the http client and the current role (see :meth:`~tests.conftest.login_role_user`)
    :param settings: The fixture providing the django settings
    :param httpserver: The fixture providing the dummy http server
    """
    # Setup a mocked Textlab API server with dummy responses
    httpserver.expect_request("/user/login").respond_with_json({"token": "dummy"})
    httpserver.expect_request("/benchmark/5").respond_with_json(
        {"formulaHix": 15.48920568}
    )

    # Redirect call aimed at the Textlab API to the fake server
    settings.TEXTLAB_API_URL = f"http://localhost:{httpserver.port}"

    # Enable Textlab in the test region
    Region.objects.filter(slug="augsburg").update(hix_enabled=True)

    # Log the user in
    client, _role = login_role_user

    # Update page content
    edit_page = reverse(
        "edit_page",
        kwargs={
            "region_slug": "augsburg",
            "language_slug": "de",
            "page_id": 2,
        },
    )

    edit_page_data = {
        "title": "Willkommen in Augsburg",
        "content": "Neuer Inhalt",
        "mirrored_page_region": "",
        "_ref_node_id": 3,
        "_position": "right",
        "status": status.PUBLIC,
    }

    response = client.post(edit_page, edit_page_data)

    assert response.status_code == 302
    assert response.headers.get("Location") == edit_page

    # Check the updated HIX score
    page_translation = Page.objects.get(id=2).get_translation("de")

    assert page_translation.hix_score == 15.48920568


@pytest.mark.django_db
@pytest.mark.parametrize("login_role_user", [EDITOR], indirect=True)
def test_hix_disable_on_region(
    load_test_data: None,
    login_role_user: tuple[Client, str],
    settings: SettingsWrapper,
    httpserver: HTTPServer,
) -> None:
    """
    Check that the HIX score is not updated when hix is disabled on region level. No request to TexLab API is expected.

    :param load_test_data: The fixture providing the test data (see :meth:`~tests.conftest.load_test_data`)
    :param login_role_user: The fixture providing the http client and the current role (see :meth:`~tests.conftest.login_role_user`)
    :param settings: The fixture providing the django settings
    :param httpserver: The fixture providing the dummy http server
    """
    # Setup a mocked Textlab API server with dummy responses
    httpserver.expect_request("/user/login").respond_with_json({"token": "dummy"})
    httpserver.expect_request("/benchmark/5").respond_with_json(
        {"formulaHix": 0.0}, status=500
    )

    # Redirect call aimed at the Textlab API to the fake server
    settings.TEXTLAB_API_URL = f"http://localhost:{httpserver.port}"

    # Disable Textlab in the test region
    Region.objects.filter(slug="augsburg").update(hix_enabled=False)

    # Log the user in
    client, _role = login_role_user

    # Update page content
    edit_page = reverse(
        "edit_page",
        kwargs={
            "region_slug": "augsburg",
            "language_slug": "de",
            "page_id": 2,
        },
    )

    edit_page_data = {
        "title": "Willkommen in Augsburg",
        "content": "Neuer Inhalt",
        "mirrored_page_region": "",
        "_ref_node_id": 3,
        "_position": "right",
        "status": status.PUBLIC,
    }

    response = client.post(edit_page, edit_page_data)

    assert response.status_code == 302
    assert response.headers.get("Location") == edit_page

    # Check that HIX score was not updated
    page_translation = Page.objects.get(id=2).get_translation("de")

    assert page_translation.hix_score == None


@pytest.mark.django_db
@pytest.mark.parametrize("login_role_user", [EDITOR], indirect=True)
def test_ignore_hix_on_page(
    load_test_data: None,
    login_role_user: tuple[Client, str],
    settings: SettingsWrapper,
    httpserver: HTTPServer,
) -> None:
    """
    Check that the HIX score is not updated when hix is disabled at the page level (hix_ignore=True). No request to TexLab API is expected.

    :param load_test_data: The fixture providing the test data (see :meth:`~tests.conftest.load_test_data`)
    :param login_role_user: The fixture providing the http client and the current role (see :meth:`~tests.conftest.login_role_user`)
    :param settings: The fixture providing the django settings
    :param httpserver: The fixture providing the dummy http server
    """
    # Setup a mocked Textlab API server with dummy responses
    httpserver.expect_request("/user/login").respond_with_json({"token": "dummy"})
    httpserver.expect_request("/benchmark/5").respond_with_json(
        {"formulaHix": 0.0}, status=500
    )

    # Redirect call aimed at the Textlab API to the fake server
    settings.TEXTLAB_API_URL = f"http://localhost:{httpserver.port}"

    # Enable Textlab in the test region
    Region.objects.filter(slug="augsburg").update(hix_enabled=True)

    # Log the user in
    client, _role = login_role_user

    # Update page content
    edit_page = reverse(
        "edit_page",
        kwargs={
            "region_slug": "augsburg",
            "language_slug": "de",
            "page_id": 2,
        },
    )

    edit_page_data = {
        "title": "Willkommen in Augsburg",
        "content": "Neuer Inhalt",
        "mirrored_page_region": "",
        "_ref_node_id": 3,
        "_position": "right",
        "status": status.PUBLIC,
        "hix_ignore": "on",
    }

    response = client.post(edit_page, edit_page_data)

    assert response.status_code == 302
    assert response.headers.get("Location") == edit_page

    # Check the updated HIX score
    page_translation = Page.objects.get(id=2).get_translation("de")

    assert page_translation.hix_score == None


@pytest.mark.django_db
@pytest.mark.parametrize("login_role_user", [EDITOR], indirect=True)
def test_hix_page_content_empty(
    load_test_data: None,
    login_role_user: tuple[Client, str],
    settings: SettingsWrapper,
    httpserver: HTTPServer,
) -> None:
    """
    Check that the HIX score is not updated when hix is enabled on page level and page content is empty. No request to TexLab API is expected.

    :param load_test_data: The fixture providing the test data (see :meth:`~tests.conftest.load_test_data`)
    :param login_role_user: The fixture providing the http client and the current role (see :meth:`~tests.conftest.login_role_user`)
    :param settings: The fixture providing the django settings
    :param httpserver: The fixture providing the dummy http server
    """
    # Setup a mocked Textlab API server with dummy responses
    httpserver.expect_request("/user/login").respond_with_json({"token": "dummy"})
    httpserver.expect_request("/benchmark/5").respond_with_json(
        {"formulaHix": 0.0}, status=500
    )

    # Redirect call aimed at the Textlab API to the fake server
    settings.TEXTLAB_API_URL = f"http://localhost:{httpserver.port}"

    # Enable Textlab in the test region
    Region.objects.filter(slug="augsburg").update(hix_enabled=True)

    # Log the user in
    client, _role = login_role_user

    # Update page content
    edit_page = reverse(
        "edit_page",
        kwargs={
            "region_slug": "augsburg",
            "language_slug": "de",
            "page_id": 2,
        },
    )

    edit_page_data = {
        "title": "Willkommen in Augsburg",
        "content": "",
        "mirrored_page_region": "",
        "_ref_node_id": 3,
        "_position": "right",
        "status": status.PUBLIC,
    }

    response = client.post(edit_page, edit_page_data)

    assert response.status_code == 302
    assert response.headers.get("Location") == edit_page

    # Check the updated HIX score
    page_translation = Page.objects.get(id=2).get_translation("de")

    assert page_translation.hix_score == None


@pytest.mark.django_db
@pytest.mark.parametrize("login_role_user", [EDITOR], indirect=True)
def test_hix_no_content_changes(
    load_test_data: None,
    login_role_user: tuple[Client, str],
    settings: SettingsWrapper,
    httpserver: HTTPServer,
) -> None:
    """
    Check that the HIX score is not updated when hix is enabled on page level and page content is not updated. No request to TexLab API is expected.

    :param load_test_data: The fixture providing the test data (see :meth:`~tests.conftest.load_test_data`)
    :param login_role_user: The fixture providing the http client and the current role (see :meth:`~tests.conftest.login_role_user`)
    :param settings: The fixture providing the django settings
    :param httpserver: The fixture providing the dummy http server
    """
    # Setup a mocked Textlab API server with dummy responses
    httpserver.expect_request("/user/login").respond_with_json({"token": "dummy"})
    httpserver.expect_request("/benchmark/5").respond_with_json(
        {"formulaHix": 0.0}, status=500
    )

    # Redirect call aimed at the Textlab API to the fake server
    settings.TEXTLAB_API_URL = f"http://localhost:{httpserver.port}"

    # Enable Textlab in the test page
    Region.objects.filter(slug="augsburg").update(hix_enabled=True)

    # Log the user in
    client, _role = login_role_user

    # Update page content
    edit_page = reverse(
        "edit_page",
        kwargs={
            "region_slug": "augsburg",
            "language_slug": "de",
            "page_id": 2,
        },
    )

    content_before_change = Page.objects.get(id=2).get_translation("de").content
    assert content_before_change != ""

    edit_page_data = {
        "title": "Neuer Titel",
        "content": content_before_change,
        "mirrored_page_region": "",
        "_ref_node_id": 3,
        "_position": "right",
        "status": status.PUBLIC,
    }

    response = client.post(edit_page, edit_page_data)

    assert response.status_code == 302
    assert response.headers.get("Location") == edit_page

    # Check the updated HIX score
    page_translation = Page.objects.get(id=2).get_translation("de")

    assert page_translation.hix_score == None


@pytest.mark.django_db
@pytest.mark.parametrize("login_role_user", [EDITOR], indirect=True)
def test_hix_response_400(
    load_test_data: None,
    login_role_user: tuple[Client, str],
    settings: SettingsWrapper,
    httpserver: HTTPServer,
) -> None:
    """
    Check that the HIX score is requested but response 400 received. Hix score is not updated

    :param load_test_data: The fixture providing the test data (see :meth:`~tests.conftest.load_test_data`)
    :param login_role_user: The fixture providing the http client and the current role (see :meth:`~tests.conftest.login_role_user`)
    :param settings: The fixture providing the django settings
    :param httpserver: The fixture providing the dummy http server
    """
    # Setup a mocked Textlab API server with dummy responses
    httpserver.expect_request("/user/login").respond_with_json({"token": "dummy"})
    httpserver.expect_request("/benchmark/5").respond_with_json(
        {"message": "Some error occured"}, status=400
    )

    # Redirect call aimed at the Textlab API to the fake server
    settings.TEXTLAB_API_URL = f"http://localhost:{httpserver.port}"

    # Enable Textlab in the test region
    Region.objects.filter(slug="augsburg").update(hix_enabled=True)

    # Log the user in
    client, _role = login_role_user

    # Update page content
    edit_page = reverse(
        "edit_page",
        kwargs={
            "region_slug": "augsburg",
            "language_slug": "de",
            "page_id": 2,
        },
    )

    edit_page_data = {
        "title": "Willkommen in Augsburg",
        "content": "Neuer Inhalt",
        "mirrored_page_region": "",
        "_ref_node_id": 3,
        "_position": "right",
        "status": status.PUBLIC,
    }

    response = client.post(edit_page, edit_page_data)

    assert response.status_code == 302
    assert response.headers.get("Location") == edit_page

    # Check the updated HIX score
    page_translation = Page.objects.get(id=2).get_translation("de")

    assert page_translation.hix_score == None
    assert False

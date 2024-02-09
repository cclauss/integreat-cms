from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from aiohttp import web
from aiohttp.web_request import BaseRequest
from aiohttp.web_response import Response
from asgiref.sync import sync_to_async
from django.test.client import AsyncClient
from django.urls import reverse
from pytest_django.fixtures import SettingsWrapper

from integreat_cms.cms.models import Page, Region

from ..conftest import (
    ANONYMOUS,
    APP_TEAM,
    CMS_TEAM,
    PRIV_STAFF_ROLES,
    ROOT,
    SERVICE_TEAM,
)
from ..utils import assert_message_in_log

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, Final

    from _pytest.logging import LogCaptureFixture

# Mapping between roles and pages used in the tests
# to avoid simultaneous translation of the same content by different users
role_pages_mapping: Final[dict[str, list[int]]] = {
    ROOT: [1, 2],
    APP_TEAM: [3, 4],
    SERVICE_TEAM: [5],
    CMS_TEAM: [6],
}


async def fake_summ_ai_server(request: BaseRequest) -> Response:
    """
    Create fake responses which simulate the SUMM.AI API server

    :param request: The request

    :return: The response
    """
    return web.json_response(
        {
            "translated_text": "Hier ist Ihre Leichte Sprache Übersetzung",
            "jobid": "9999",
        }
    )


@sync_to_async
def enable_summ_api(region_slug: str) -> None:
    """
    Enable SUMM.AI in the test region

    :param region_slug: The slug of the region in which we want to enable SUMM.AI
    """
    # Enable SUMM.AI in the test region without changing last_updated field
    # to prevent race conditions with other tests
    Region.objects.filter(slug=region_slug).update(summ_ai_enabled=True)


@sync_to_async
def get_changed_pages(
    settings: SettingsWrapper, ids: list[int]
) -> list[dict[str, Any]]:
    """
    Load the changed pages with the specified ids from the database

    :param settings: The fixture providing the django settings
    :param ids: A list containing the requested pages including their translations in German and Easy German

    :return: The changed pages
    """
    # Enable SUMM.AI in the test region
    return [
        {
            "page": page,
            **{
                slug: page.get_translation(slug)
                for slug in [
                    settings.SUMM_AI_GERMAN_LANGUAGE_SLUG,
                    settings.SUMM_AI_EASY_GERMAN_LANGUAGE_SLUG,
                ]
            },
        }
        for page in Page.objects.filter(id__in=ids)
    ]


@pytest.mark.django_db
async def test_auto_translate_easy_german(
    login_role_user_async: tuple[AsyncClient, str],
    settings: SettingsWrapper,
    aiohttp_raw_server: Callable,
    caplog: LogCaptureFixture,
) -> None:
    """
    This test checks whether the SUMM.AI API client works as expected

    :param login_role_user_async: The fixture providing the http client and the current role (see :meth:`~tests.conftest.login_role_user`)
    :param settings: The fixture providing the django settings
    :param aiohttp_raw_server: The fixture providing the dummy aiohttp server used for faking the SUMM.AI API server
    :param caplog: The :fixture:`caplog` fixture
    """
    # The region we want to use for testing
    region_slug = "augsburg"
    # Enable SUMM.AI in the test region
    await enable_summ_api(region_slug)
    # Setup a dummy server to fake responses from the SUMM.AI API server (an instance of aiohttp.test_utils.RawTestServer)
    fake_server = await aiohttp_raw_server(fake_summ_ai_server)
    # Redirect call to the SUMM.AI API to the fake server
    settings.SUMM_AI_API_URL = (
        f"{fake_server.scheme}://{fake_server.host}:{fake_server.port}"
    )
    # Test for english messages
    settings.LANGUAGE_CODE = "en"
    # Log the user in
    client, role = login_role_user_async
    # Translate the pages
    selected_ids = role_pages_mapping.get(role, [1])

    translate_easy_german = reverse(
        "machine_translation_pages",
        kwargs={
            "region_slug": region_slug,
            "language_slug": settings.SUMM_AI_EASY_GERMAN_LANGUAGE_SLUG,
        },
    )
    response = await client.post(
        translate_easy_german, data={"selected_ids[]": selected_ids}
    )
    print(response.headers)
    if role in PRIV_STAFF_ROLES:
        # If the role should be allowed to access the view, we expect a successful result
        assert response.status_code == 302
        page_tree = reverse(
            "pages",
            kwargs={
                "region_slug": region_slug,
                "language_slug": settings.SUMM_AI_EASY_GERMAN_LANGUAGE_SLUG,
            },
        )
        assert response.headers.get("Location") == page_tree
        response = await client.get(page_tree)
        print(response.headers)
        # Get the page objects including their translations from the database
        changed_pages = await get_changed_pages(settings, selected_ids)
        for page in changed_pages:
            # Check that the success message are present
            assert_message_in_log(
                f'SUCCESS  Page "{page[settings.SUMM_AI_GERMAN_LANGUAGE_SLUG]}" has been successfully translated into Easy German.',
                caplog,
            )
            # Check that the page translation exists and really has the correct content
            assert (
                "Hier ist Ihre Leichte Sprache Übersetzung"
                in page[settings.SUMM_AI_EASY_GERMAN_LANGUAGE_SLUG].content
            )
    elif role == ANONYMOUS:
        # For anonymous users, we want to redirect to the login form instead of showing an error
        assert response.status_code == 302
        assert (
            response.headers.get("location")
            == f"{settings.LOGIN_URL}?next={translate_easy_german}"
        )
    else:
        # For logged in users, we want to show an error if they get a permission denied
        assert response.status_code == 403


async def broken_fake_summ_ai_server(request: BaseRequest) -> Response:
    """
    Create fake responses which simulate the SUMM.AI API server

    :param request: The request

    :return: The response
    """
    return web.json_response(
        data={
            "error": "An error occurred",
        },
        status=500,
    )


@pytest.mark.django_db
async def test_summ_ai_error_handling(
    login_role_user_async: tuple[AsyncClient, str],
    settings: SettingsWrapper,
    aiohttp_raw_server: Callable,
    caplog: LogCaptureFixture,
) -> None:
    """
    This test checks whether the error handling of the SUMM.AI API client works as expected

    :param login_role_user_async: The fixture providing the http client and the current role (see :meth:`~tests.conftest.login_role_user`)
    :param settings: The fixture providing the django settings
    :param aiohttp_raw_server: The fixture providing the dummy aiohttp server used for faking the SUMM.AI API server
    :param caplog: The :fixture:`caplog` fixture
    """
    # The region we want to use for testing
    region_slug = "augsburg"
    # Setup a dummy server to fake responses from the SUMM.AI API server (an instance of aiohttp.test_utils.RawTestServer)
    fake_server = await aiohttp_raw_server(broken_fake_summ_ai_server)
    # Enable SUMM.AI in the test region
    await enable_summ_api(region_slug)
    # Redirect call to the SUMM.AI API to the fake server
    settings.SUMM_AI_API_URL = (
        f"{fake_server.scheme}://{fake_server.host}:{fake_server.port}"
    )
    # Test for english messages
    settings.LANGUAGE_CODE = "en"
    # Log the user in
    client, role = login_role_user_async
    # Translate the pages
    translate_easy_german = reverse(
        "machine_translation_pages",
        kwargs={
            "region_slug": region_slug,
            "language_slug": settings.SUMM_AI_EASY_GERMAN_LANGUAGE_SLUG,
        },
    )

    ready_for_mt_page_id = 14
    response = await client.post(
        translate_easy_german, data={"selected_ids[]": [ready_for_mt_page_id]}
    )
    print(response.headers)

    if role in PRIV_STAFF_ROLES:
        # If the role should be allowed to access the view, we expect a redirect to the page tree
        assert response.status_code == 302
        page_tree = reverse(
            "pages",
            kwargs={
                "region_slug": region_slug,
                "language_slug": settings.SUMM_AI_EASY_GERMAN_LANGUAGE_SLUG,
            },
        )
        assert response.headers.get("Location") == page_tree
        response = await client.get(page_tree)
        print(response.headers)
        # Check that the error message is present
        assert_message_in_log(
            'ERROR    Page "Behörden und Beratung" could not be automatically translated into Easy German. '
            "Please try again later or contact an administrator.",
            caplog,
        )

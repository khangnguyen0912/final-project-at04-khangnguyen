import json
import logging
from pathlib import Path
import pytest
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from api.core.endpoints import LOGIN
from config import API_BASE_URL, DEFAULT_TIMEOUT, EMAIL, PASSWORD, UI_TIMEOUT
from pages.base_page import BasePage
from utils.logging_setup import configure_test_logging

pytest_plugins = ("tests.pytest_hooks",)

SCREENSHOTS_DIR = Path(__file__).resolve().parents[1] / "screenshots"
LOGS_DIR = Path(__file__).resolve().parents[1] / "logs"
LOGGER = logging.getLogger(__name__)
BROWSER_VIEWPORT = {"width": 1920, "height": 1080}


@pytest.fixture(scope="session", autouse=True)
def configure_logging_for_test_session(request):
    log_file_path = configure_test_logging(LOGS_DIR)
    cleanup_result = getattr(request.config, "_screenshots_cleanup_result", None)
    LOGGER.info("Test logging initialized: %s", log_file_path)
    if cleanup_result is not None:
        cleaned_dir, removed_items = cleanup_result
        LOGGER.info("Cleared screenshots directory: %s (removed=%d)", cleaned_dir, removed_items)
    yield
    LOGGER.info("Test session finished.")


def resolve_test_case_name(node):
    callspec = getattr(node, "callspec", None)
    if callspec is not None and getattr(callspec, "id", None):
        return str(callspec.id)
    return str(node.name)


@pytest.fixture(scope="session")
def account_state():
    return {"email": EMAIL, "password": PASSWORD}


@pytest.fixture(scope="function")
async def api_request():
    if not API_BASE_URL:
        raise ValueError("Missing API_BASE_URL in .env")

    async with async_playwright() as playwright:
        request = await playwright.request.new_context(
            base_url=API_BASE_URL.rstrip("/"),
            extra_http_headers={"Content-Type": "application/json"},
            timeout=DEFAULT_TIMEOUT,
        )
        try:
            yield request
        finally:
            await request.dispose()


@pytest.fixture(scope="function")
async def access_token(api_request, account_state):
    payload = {
        "email": account_state["email"],
        "password": account_state["password"],
    }
    response = await api_request.post(
        LOGIN,
        data=json.dumps(payload),
        timeout=DEFAULT_TIMEOUT,
    )
    try:
        body = await response.json()
    except Exception:
        body = {"raw_text": await response.text()}

    token = body.get("accessToken") if isinstance(body, dict) else None
    if not token:
        pytest.fail(
            "Cannot get access token for API tests. "
            f"status={response.status}, response={body}. "
            "Check current account_state credentials in this test session."
        )
    return token


@pytest.fixture(scope="function")
def ui_page(request):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(viewport=BROWSER_VIEWPORT)
        page = context.new_page()
        page.set_default_timeout(UI_TIMEOUT)
        page.set_default_navigation_timeout(UI_TIMEOUT)
        try:
            yield page
        finally:
            setup_report = getattr(request.node, "rep_setup", None)
            call_report = getattr(request.node, "rep_call", None)
            failed = bool(
                (setup_report is not None and setup_report.failed)
                or (call_report is not None and call_report.failed)
            )

            if failed and not page.is_closed():
                screenshot_path = BasePage(page).take_screenshot(
                    resolve_test_case_name(request.node),
                    folder=SCREENSHOTS_DIR,
                )
                LOGGER.error("Saved failure screenshot: %s", screenshot_path)

            context.close()
            browser.close()

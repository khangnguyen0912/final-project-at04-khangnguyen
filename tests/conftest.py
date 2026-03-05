import json
from pathlib import Path
import pytest
import requests
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from api.core.endpoints import LOGIN, REGISTER
from config import API_BASE_URL, DEFAULT_TIMEOUT, EMAIL, PASSWORD, UI_TIMEOUT
from pages.base_page import BasePage

SCREENSHOTS_DIR = Path(__file__).resolve().parents[1] / "screenshots"


def _resolve_test_case_name(node):
    callspec = getattr(node, "callspec", None)
    if callspec is not None and getattr(callspec, "id", None):
        return str(callspec.id)
    return str(node.name)

@pytest.fixture(scope="session")
def account_state():
    state = {"email": EMAIL, "password": PASSWORD}

    if not API_BASE_URL or not EMAIL or not PASSWORD:
        return state

    base_url = API_BASE_URL.rstrip("/")
    login_url = f"{base_url}{LOGIN}"
    register_url = f"{base_url}{REGISTER}"
    timeout_sec = max(DEFAULT_TIMEOUT, 5000) / 1000

    def can_login(email: str, password: str) -> bool:
        try:
            response = requests.post(
                login_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps({"email": email, "password": password}),
                timeout=timeout_sec,
            )
            body = response.json()
        except Exception:
            return False
        token = body.get("accessToken") if isinstance(body, dict) else None
        return bool(token)

    if can_login(EMAIL, PASSWORD):
        return state

    # Try to recreate default account when credentials changed by earlier tests
    register_payload = {
        "name": "Automation User",
        "email": EMAIL,
        "password": PASSWORD,
        "avatarUrl": "https://i.pinimg.com/736x/8f/0b/5c/8f0b5c33cf99d078cd8945492520b7e6.jpg",
        "phone": "0990111222",
        "address": "59 Ly Thai To, Phuong Vuon Lai, Thanh pho Ho Chi Minh",
    }
    try:
        requests.post(
            register_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(register_payload),
            timeout=timeout_sec,
        )
    except Exception:
        pass

    if can_login(EMAIL, PASSWORD):
        return state

    for candidate in ("Kh@ng_qa1234", "Kh@ng_qa12345", "Kh@ng_qa123456", "Kh@ng_qa1995"):
        if candidate == PASSWORD:
            continue
        if can_login(EMAIL, candidate):
            state["password"] = candidate
            break

    return state


@pytest.fixture(scope="function", autouse=True)
def ensure_default_account_after_test_case():
    yield

    if not API_BASE_URL or not EMAIL or not PASSWORD:
        return

    base_url = API_BASE_URL.rstrip("/")
    login_url = f"{base_url}{LOGIN}"
    register_url = f"{base_url}{REGISTER}"
    timeout_sec = max(DEFAULT_TIMEOUT, 5000) / 1000

    try:
        login_response = requests.post(
            login_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"email": EMAIL, "password": PASSWORD}),
            timeout=timeout_sec,
        )
        login_body = login_response.json()
        if isinstance(login_body, dict) and login_body.get("accessToken"):
            return
    except Exception:
        pass

    register_payload = {
        "name": "Automation User",
        "email": EMAIL,
        "password": PASSWORD,
        "avatarUrl": "https://i.pinimg.com/736x/8f/0b/5c/8f0b5c33cf99d078cd8945492520b7e6.jpg",
        "phone": "0990111222",
        "address": "59 Ly Thai To, Phuong Vuon Lai, Thanh pho Ho Chi Minh",
    }
    try:
        requests.post(
            register_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(register_payload),
            timeout=timeout_sec,
        )
    except Exception:
        pass


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
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
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
                    _resolve_test_case_name(request.node),
                    folder=SCREENSHOTS_DIR,
                )
                print(f"\n[ui_page] Saved failure screenshot: {screenshot_path}")

            context.close()
            browser.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

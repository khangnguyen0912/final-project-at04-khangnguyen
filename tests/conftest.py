from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import allure
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
import pytest
import requests
from api.core.endpoints import LOGIN, REGISTER
from config import (
    API_BASE_URL,
    EMAIL,
    PASSWORD,
    DEFAULT_TIMEOUT,
    UI_TIMEOUT,
    STEP_PAUSE,
)
from pages.sign_in_page import SignInPage

screenshot_dir = Path(__file__).resolve().parents[1] / "screenshots"
screenshot_dir.mkdir(parents=True, exist_ok=True)
screenshots_cleared = False

REGISTER_PAYLOAD = {
    "name": "Khang Nguyen",
    "email": "mkhang0995.it@gmail.com",
    "password": "Kh@ng_qa1234",
    "avatarUrl": "https://i.pinimg.com/736x/8f/0b/5c/8f0b5c33cf99d078cd8945492520b7e6.jpg",
    "phone": "0990111222",
    "address": "59 Lý Thái Tổ, Phường Vườn Lài, Thành phố Hồ Chí Minh",
}

KNOWN_PASSWORD_CANDIDATES = [
    "Kh@ng_qa1234",
    "Kh@ng_qa12345",
    "Kh@ng_qa123456",
    "Kh@ng_qa1995",
]


def _require_api_base_url():
    if not API_BASE_URL:
        raise ValueError("Missing API_BASE_URL in .env")
    return API_BASE_URL.rstrip("/")


def _register_default_user_after_run():
    if not API_BASE_URL:
        return

    base_url = _require_api_base_url()
    register_url = f"{base_url}{REGISTER}"
    timeout_sec = max(DEFAULT_TIMEOUT, 5000) / 1000

    try:
        requests.post(
            register_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(REGISTER_PAYLOAD),
            timeout=timeout_sec,
        )
    except Exception:
        return


def _try_login_sync(email: str, password: str):
    if not email or not password or not API_BASE_URL:
        return False, None, None

    login_url = f"{_require_api_base_url()}{LOGIN}"
    timeout_sec = max(DEFAULT_TIMEOUT, 5000) / 1000

    try:
        response = requests.post(
            login_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"email": email, "password": password}),
            timeout=timeout_sec,
        )
    except Exception as exc:
        return False, None, str(exc)

    try:
        body = response.json()
    except Exception:
        body = response.text

    token = body.get("accessToken") if isinstance(body, dict) else None
    return bool(token), response.status_code, body


def _bootstrap_account_state():
    state = {"email": EMAIL, "password": PASSWORD}

    if not EMAIL or not PASSWORD or not API_BASE_URL:
        return state

    ok, _, _ = _try_login_sync(EMAIL, PASSWORD)
    if ok:
        return state

    # Ensure default account exists if previous run changed email away from default.
    _register_default_user_after_run()
    ok, _, _ = _try_login_sync(EMAIL, PASSWORD)
    if ok:
        return state

    # If register returns "email exists", password may differ from .env.
    checked = set()
    for candidate in [PASSWORD, *KNOWN_PASSWORD_CANDIDATES]:
        if not candidate or candidate in checked:
            continue
        checked.add(candidate)
        ok, _, _ = _try_login_sync(EMAIL, candidate)
        if ok:
            state["password"] = candidate
            return state

    return state


def _ensure_default_account_after_each_test():
    if not API_BASE_URL or not EMAIL or not PASSWORD:
        return

    ok, _, _ = _try_login_sync(EMAIL, PASSWORD)
    if ok:
        return

    _register_default_user_after_run()


def take_screenshot(item, page):
    label = None
    callspec = getattr(item, "callspec", None)
    if callspec:
        params = getattr(callspec, "params", {}) or {}
        updates = []
        for field in ("name", "email", "phone"):
            if field not in params:
                continue
            raw_value = params[field]
            if raw_value is None:
                continue
            if isinstance(raw_value, str) and raw_value.strip().upper() == "EMPTY":
                value = "EMPTY"
            else:
                value = str(raw_value).strip()
            if value == "":
                value = "EMPTY"
            if len(value) > 32:
                value = value[:29] + "..."
            updates.append(f"{field}-{value}")
        if updates:
            label = " ".join(updates)

    if not label:
        label = item.name.strip()

    test_name = re.sub(r'[\\/:*?"<>|]+', "-", label)
    test_name = re.sub(r"\s+", " ", test_name).strip()
    if len(test_name) > 120:
        test_name = test_name[:117] + "..."

    failed_at = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    screenshot_name = f"{test_name} {failed_at}.png"
    screenshot_path = screenshot_dir / screenshot_name

    try:
        page.screenshot(path=str(screenshot_path), full_page=True)
        allure.attach.file(
            str(screenshot_path),
            name=screenshot_name,
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception as exc:
        allure.attach(
            str(exc),
            name=f"{item.name} - screenshot error",
            attachment_type=allure.attachment_type.TEXT,
        )

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    if report.when != "call" or not report.failed:
        return

    if not getattr(item, "_enable_failure_screenshot", False):
        return

    page = None
    for fixture_name in ("ui_page", "logged_in_page", "page"):
        if fixture_name in getattr(item, "funcargs", {}):
            page = item.funcargs[fixture_name]
            break

    if page is None:
        return

    take_screenshot(item, page)


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    occupied = set()

    for item in items:
        nodeid = item.nodeid
        short_nodeid = None

        is_target_file = (
            nodeid.startswith("tests/api/api_patch_profile/single_field/")
            or nodeid.startswith("tests/ui/test_update_profile.py")
        )
        if is_target_file and nodeid.endswith("]") and "[" in nodeid and "::" in nodeid:
            path = nodeid.split("::", 1)[0]
            case_id = nodeid.rsplit("[", 1)[1][:-1]
            short_nodeid = f"{path}::[{case_id}]"

        if short_nodeid:
            candidate = short_nodeid
            index = 2
            while candidate in occupied:
                candidate = f"{short_nodeid}#{index}"
                index += 1
            item._nodeid = candidate
            occupied.add(candidate)
        else:
            occupied.add(nodeid)


@pytest.fixture(scope="function", autouse=True)
def take_screenshot_of_failure(request):
    global screenshots_cleared


    if not screenshots_cleared and not os.environ.get("PYTEST_XDIST_WORKER"):
        for entry in screenshot_dir.iterdir():
            if entry.is_file() or entry.is_symlink():
                entry.unlink(missing_ok=True)
            elif entry.is_dir():
                shutil.rmtree(entry, ignore_errors=True)
        screenshots_cleared = True
    request.node._enable_failure_screenshot = True
    yield


@pytest.fixture(scope="function", autouse=True)
def ensure_default_account_after_test_case():
    yield
    _ensure_default_account_after_each_test()


@pytest.fixture(scope="session")
def account_state():
    return _bootstrap_account_state()


@pytest.fixture(scope="function")
async def api_request():
    api_base_url = _require_api_base_url()
    async with async_playwright() as p:
        request = await p.request.new_context(
            base_url=api_base_url,
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
def logged_in_page(account_state):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        page.set_default_timeout(UI_TIMEOUT)
        page.set_default_navigation_timeout(UI_TIMEOUT)
        try:
            sign_in_page = SignInPage(page)
            sign_in_page.open(timeout=UI_TIMEOUT)
            try:
                sign_in_page.is_login_page_loaded(timeout=UI_TIMEOUT)
            except Exception as exc:
                page_title = "<unknown>"
                try:
                    page_title = page.title()
                except Exception:
                    pass
                raise AssertionError(
                    f"Login page is not ready. current_url={page.url}, title={page_title!r}"
                ) from exc
            sign_in_page.login(account_state["email"], account_state["password"])
            yield page
        except Exception:
            try:
                allure.attach(page.url, "UI setup current URL", allure.attachment_type.TEXT)
            except Exception:
                pass
            try:
                allure.attach(
                    page.title(),
                    "UI setup current page title",
                    allure.attachment_type.TEXT,
                )
            except Exception:
                pass
            try:
                allure.attach(
                    page.screenshot(full_page=True),
                    "UI setup failure screenshot",
                    allure.attachment_type.PNG,
                )
            except Exception:
                pass
            raise
        finally:
            context.close()
            browser.close()


@pytest.fixture(scope="function")
def ui_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        page.set_default_timeout(UI_TIMEOUT)
        page.set_default_navigation_timeout(UI_TIMEOUT)
        try:
            yield page
        finally:
            context.close()
            browser.close()

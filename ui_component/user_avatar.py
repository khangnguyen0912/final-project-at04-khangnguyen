from playwright.sync_api import Page
from config import UI_TIMEOUT

class UserAvatar:

    _avatar = '//button[@type="button"][.//div[contains(@class,"MuiAvatar-root")]]'
    _profile_option = '//li[normalize-space()="Profile"]'
    _settings_option = '//li[normalize-space()="Settings"]'
    _logout_button = '//button[normalize-space()="Logout"]'

    def __init__(self, page: Page):
        self.page = page
        self._avatar_el = page.locator(self._avatar)
        self._profile_option_el = page.locator(self._profile_option)
        self._settings_option_el = page.locator(self._settings_option)
        self._logout_button_el = page.locator(self._logout_button)

    def go_to_my_profile_page(self):
        timeout = max(UI_TIMEOUT, 12000)
        self._avatar_el.first.wait_for(state="visible", timeout=timeout)
        self._avatar_el.first.click(timeout=timeout)
        try:
            self._profile_option_el.wait_for(state="visible", timeout=timeout)
        except Exception:
            self.page.wait_for_timeout(250)
            self._avatar_el.first.click(timeout=timeout)
            self._profile_option_el.wait_for(state="visible", timeout=timeout)
        self._profile_option_el.first.click(timeout=timeout)

    def go_to_settings_account_page(self):
        timeout = max(UI_TIMEOUT, 12000)
        self._avatar_el.first.wait_for(state="visible", timeout=timeout)
        self._avatar_el.first.click(timeout=timeout)
        self._settings_option_el.wait_for(state="visible", timeout=timeout)
        self._settings_option_el.first.click(timeout=timeout)

    def log_out(self):
        timeout = max(UI_TIMEOUT, 12000)
        self._avatar_el.first.wait_for(state="visible", timeout=timeout)
        self._avatar_el.first.click(timeout=timeout)
        self._logout_button_el.wait_for(state="visible", timeout=timeout)
        self._logout_button_el.first.click(timeout=timeout)

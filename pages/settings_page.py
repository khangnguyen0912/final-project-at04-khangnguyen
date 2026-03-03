from playwright.sync_api import Page, expect
from config import UI_TIMEOUT
from pages.base_page import BasePage
from ui_component.user_avatar import UserAvatar

class SettingsAccountPage(BasePage):


    _settings_account_title = '//h4[normalize-space()="Setting account"]'
    _settings_account_text = '//p[text()="Setting account"]'


    _span_theme_title = '//span[text()="Theme"]'
    _light_tab_theme_button = '//button[@type="button" and @role="tab" and text()="Light"]'
    _dark_tab_theme_button = '//button[@type="button" and @role="tab" and text()="Dark"]'
    _system_tab_theme_button = '//button[@type="button" and @role="tab" and text()="System"]'


    _span_select_color_title = '//span[text()="Select color"]'


    _reset_btn = '//button[text()="Reset"]'
    _save_btn = '//button[text()="Save"]'


    _my_profile = '//a[contains(@href,"my-profile")]//p'

    def __init__(self, page: Page):
        super().__init__(page)
        self.user_avatar = UserAvatar(page)

    def open_settings_account_page(self):
        self.user_avatar.go_to_settings_account_page()

    def click_save_profile(self, require_enabled=True):
        save_btn = self.page.locator(self._save_btn)
        if require_enabled:
            expect(save_btn).to_be_enabled(timeout=UI_TIMEOUT)
            save_btn.click(timeout=UI_TIMEOUT)
            return
        save_btn.click(force=True, timeout=UI_TIMEOUT)

    def is_settings_account_page_loaded(self):
        expect(self.page.locator(self._settings_account_title)).to_be_visible(timeout=UI_TIMEOUT)
        expect(self.page.locator(self._settings_account_text)).to_be_visible(timeout=UI_TIMEOUT)
        expect(self.page.locator(self._span_theme_title)).to_be_visible(timeout=UI_TIMEOUT)
        expect(self.page.locator(self._span_select_color_title)).to_be_visible(timeout=UI_TIMEOUT)
        expect(self.page.locator(self._reset_btn)).to_be_visible(timeout=UI_TIMEOUT)
        expect(self.page.locator(self._save_btn)).to_be_visible(timeout=UI_TIMEOUT)

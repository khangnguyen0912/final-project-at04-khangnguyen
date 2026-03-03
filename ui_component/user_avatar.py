from playwright.sync_api import Page

class UserAvatar:

    _avatar = '//button[@type="button"]//div[contains(@class,"MuiAvatar-root")]'
    _profile_option = '//li[text()="Profile"]'
    _settings_option = '//li[text()="Settings"]'
    _logout_button = '//button[text()="Logout"]'

    def __init__(self, page: Page):
        self.page = page
        self._avatar_el = page.locator(self._avatar)
        self._profile_option_el = page.locator(self._profile_option)
        self._settings_option_el = page.locator(self._settings_option)
        self._logout_button_el = page.locator(self._logout_button)

    def go_to_my_profile_page(self):
        self._avatar_el.click()
        self._profile_option_el.click()

    def go_to_settings_account_page(self):
        self._avatar_el.click()
        self._settings_option_el.click()

    def log_out(self):
        self._avatar_el.click()
        self._logout_button_el.click()

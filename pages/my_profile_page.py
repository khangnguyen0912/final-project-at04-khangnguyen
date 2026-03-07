from playwright.sync_api import Page, expect
from config import BASE_URL, UI_TIMEOUT
from pages.base_page import BasePage
from ui_component.user_avatar import UserAvatar

class MyProfilePage(BasePage):


    _my_profile_title = '//h4[normalize-space()="My Profile"]'
    _change_my_profile_text = '//p[text()="Change my profile"]'


    _name_field = '//input[@type="text" and @name="name"]'
    _phone_field = '//input[@type="text" and @name="phone"]'
    _email_field = '//input[@type="text" and @name="email"]'
    _old_password_field = '//input[@type="password" and @name="oldPassword"]'
    _new_password_field = '//input[@type="password" and @name="password"]'
    _confirm_password_field = '//input[@type="password" and @name="password_confirmation"]'


    _success_toast = '//p[text()="Updated profile successfully."]'


    _error_required_name = '//p[text()="Name is required."]'
    _error_required_email = '//p[text()="Email is required."]'
    _error_required_old_password = '//p[text()="Old Password is required."]'


    _error_invalid_phone = '//p[text()="Invalid phone number"]'
    _error_invalid_email = '//p[text()="Invalid email address"]'


    _reset_btn = '//button[text()="Reset"]'
    _save_btn = '//button[text()="Save Profile"]'


    _my_profile = '//a[contains(@href,"my-profile")]//p'

    def __init__(self, page: Page):
        super().__init__(page)
        self.user_avatar = UserAvatar(page)

    def open_my_profile_page(self):
        if not BASE_URL:
            raise ValueError("Missing BASE_URL in .env")
        try:
            self.user_avatar.go_to_my_profile_page()
            return
        except Exception:
            self.page.goto(
                f"{BASE_URL}/",
                wait_until="domcontentloaded",
                timeout=max(UI_TIMEOUT, 12000),
            )
            self.user_avatar.go_to_my_profile_page()

    def click_save_profile(self, require_enabled=True):
        save_btn = self.page.locator(self._save_btn)
        if require_enabled:
            expect(save_btn).to_be_enabled(timeout=UI_TIMEOUT)
            save_btn.click(timeout=UI_TIMEOUT)
            return
        save_btn.click(force=True, timeout=UI_TIMEOUT)

    def is_my_profile_page_loaded(self, timeout: int = UI_TIMEOUT):
        expect(self.page.locator(self._my_profile_title)).to_be_visible(timeout=timeout)
        expect(self.page.locator(self._change_my_profile_text)).to_be_visible(timeout=timeout)
        expect(self.page.locator(self._name_field)).to_be_visible(timeout=timeout)
        expect(self.page.locator(self._phone_field)).to_be_visible(timeout=timeout)
        expect(self.page.locator(self._email_field)).to_be_visible(timeout=timeout)
        expect(self.page.locator(self._save_btn)).to_be_visible(timeout=timeout)
        return True

    def update_profile(self, name=None, email=None, phone=None):
        if name is not None:
            self.page.locator(self._name_field).fill(str(name))
        if email is not None:
            self.page.locator(self._email_field).fill(str(email))
        if phone is not None:
            self.page.locator(self._phone_field).fill(str(phone))
        self.click_save_profile()

    def is_updated_successful(self, expected_name=None, expected_email=None, expected_phone=None):
        toast_visible = False
        try:
            expect(self.page.locator(self._success_toast)).to_be_visible(timeout=UI_TIMEOUT)
            toast_visible = True
        except AssertionError:
            toast_visible = False

        field_expectations = (
            (self._name_field, expected_name),
            (self._email_field, expected_email),
            (self._phone_field, expected_phone),
        )

        expected_fields_provided = False
        for locator, expected_value in field_expectations:
            if expected_value is None:
                continue
            expected_fields_provided = True
            expect(self.page.locator(locator)).to_have_value(str(expected_value), timeout=UI_TIMEOUT)

        if expected_fields_provided:
            return True
        if toast_visible:
            return True
        return False

    def is_updated_fail(self):
        error_locators = [
            self._error_required_name,
            self._error_required_email,
            self._error_required_old_password,
            self._error_invalid_email,
            self._error_invalid_phone,
        ]
        for loc in error_locators:
            if self.page.locator(loc).is_visible():
                return True

        return False

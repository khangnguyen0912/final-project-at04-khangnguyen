from playwright.sync_api import Page, expect
from config import BASE_URL, UI_TIMEOUT
from pages.base_page import BasePage

class SignInPage(BasePage):

    _sign_in_title = '//h3[text()="Sign in"]'
    _email_field = '//input[@name="email"]'
    _password_field = '//input[@name="password"]'
    _login_account_button = '//button[normalize-space()="Login account"]'
    
    _toast_error_invalid_password = '//p[text()="Invalid password."]'
    _toast_error_user_not_found = '//p[text()="User not found."]'

    def __init__(self, page: Page):
        super().__init__(page)
        self._toast_invalid = page.locator('//div[text()="Invalid Login Credentials."]')
        self._my_profile = page.locator('//a[contains(@href,"my-profile")]//p')

    def open(self, timeout: int = UI_TIMEOUT):

        if not BASE_URL:
            raise ValueError("Missing BASE_URL in .env")
        sign_in_url = f"{BASE_URL}/sign-in"
        self.page.goto(sign_in_url, wait_until="domcontentloaded", timeout=timeout)

    def is_login_page_loaded(self, timeout: int = UI_TIMEOUT):
        expect(self.page.locator(self._sign_in_title)).to_be_visible(timeout=timeout)
        expect(self.page.locator(self._email_field)).to_be_visible(timeout=timeout)
        expect(self.page.locator(self._password_field)).to_be_visible(timeout=timeout)
        expect(self.page.locator(self._login_account_button)).to_be_visible(timeout=timeout)

    def login(self, email, password):
        self.page.locator(self._email_field).fill(email)
        self.page.locator(self._password_field).fill(password)
        self.page.locator(self._login_account_button).click()

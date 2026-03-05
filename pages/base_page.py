import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import Page
from config import UI_TIMEOUT

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def click(self, locator):
        self.page.locator(locator).click()

    def fill(self, locator, text):
        self.page.locator(locator).fill(text)

    def get_text(self, locator):
        return self.page.locator(locator).inner_text()

    def take_screenshot(self, test_name: str, folder: str | Path | None = None):
        screenshots_dir = (
            Path(folder)
            if folder is not None
            else Path(__file__).resolve().parents[1] / "screenshots"
        )
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        safe_test_name = re.sub(r"[^a-z0-9]+", "_", test_name.lower()).strip("_")

        exec_datetime = datetime.now().strftime("%b%d_%Y_%H%M%S").lower()
        base_filename = f"{safe_test_name}_{exec_datetime}"
        screenshot_path = screenshots_dir / f"{base_filename}.png"
        duplicate_index = 1
        while screenshot_path.exists():
            screenshot_path = screenshots_dir / f"{base_filename}_{duplicate_index}.png"
            duplicate_index += 1

        self.page.screenshot(path=str(screenshot_path), full_page=True)
        return str(screenshot_path)

    def is_visible(self, locator):
        return self.page.locator(locator).is_visible()

    def hover(self, locator):
        self.page.locator(locator).hover()

    def reload_page(self):
        self.page.reload(wait_until="domcontentloaded")

    def clear_field(self, field_locator):
        field = self.page.locator(field_locator)
        field.click()
        field.fill("")

    def fill_field(self, field_locator, value):
        self.page.locator(field_locator).fill(str(value))

import re

from playwright.sync_api import expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/login/"

    @property
    def email_input(self):
        return self.page.locator("#email")

    @property
    def password_input(self):
        return self.page.locator("#password")

    @property
    def submit_button(self):
        return self.page.get_by_role("button", name=re.compile(r"^log in$", re.I)).first

    @property
    def error_message(self):
        return self.page.locator(
            '[role="alert"], [data-test-id*="error" i], [id$="-error"]'
        ).first

    def login(self, email: str, password: str):
        self.page.wait_for_load_state("load")
        expect(self.email_input).to_be_visible()
        self.email_input.click()
        self.email_input.press_sequentially(email, delay=40)
        self.password_input.click()
        self.password_input.press_sequentially(password, delay=40)
        expect(self.submit_button).to_be_enabled()
        self.submit_button.click()
        return self

    def wait_until_logged_in(self, timeout: int = 30000):
        try:
            expect(self.account_menu_button).to_be_visible(timeout=timeout)
        except AssertionError:
            if self.error_message.count():
                detail = self.error_message.inner_text()
            else:
                detail = "повідомлення про помилку на сторінці відсутнє"
            raise AssertionError(
                f"Вхід не завершився (URL: {self.page.url}). "
                f"Текст помилки на сторінці: {detail!r}. "
                f"Імовірно, перевірка безпеки (CAPTCHA) або невірні дані в .env."
            ) from None

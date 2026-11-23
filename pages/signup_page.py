import re

from playwright.sync_api import expect

from pages.base_page import BasePage


class SignupPage(BasePage):
    path = "/"

    @property
    def email_input(self):
        return self.page.get_by_role("textbox", name="Email").first

    @property
    def password_input(self):
        return self.page.get_by_role("textbox", name="Password").first

    @property
    def email_error(self):
        return (
            self.page.get_by_role("alert")
            .filter(has_text=re.compile(r"valid email|not an email|email address", re.I))
            .first
        )

    @property
    def password_error(self):
        return self.page.get_by_text(re.compile(r"more complicated", re.I)).first

    @property
    def password_meter(self):
        return self.page.get_by_role("meter", name=re.compile(r"password strength", re.I))

    @property
    def continue_button(self):
        return self.page.get_by_role(
            "button", name=re.compile(r"continue creating your pinterest account", re.I)
        )

    def open_form(self):
        """Відкриває форму реєстрації (без створення акаунта)."""
        self.open_page("/")
        self.page.get_by_role("button", name=re.compile(r"^sign up$", re.I)).first.click()
        expect(self.email_input).to_be_visible()
        return self

    def fill_credentials(self, email: str, password: str):
        self.email_input.fill(email)
        self.password_input.fill(password)

    def blur(self):
        """Прибирає фокус із полів, щоб спрацювала валідація."""
        self.page.get_by_role("heading", name="Welcome to Pinterest").click()

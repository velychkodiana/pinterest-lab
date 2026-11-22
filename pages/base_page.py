from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from config import settings


class BasePage:
    path = "/"

    def __init__(self, page: Page):
        self.page = page
        self.page.set_default_timeout(settings.DEFAULT_TIMEOUT)

    # --- спільні елементи шапки ---
    @property
    def search_input(self):
        return (
            self.page.locator('input[name="searchBoxInput"]')
            .or_(self.page.get_by_role("combobox", name=re.compile("search", re.I)))
            .first
        )

    @property
    def account_menu_button(self):
        return (
            self.page.get_by_role("banner")
            .get_by_role("button", name=re.compile(r"^Accounts( and more options)?$", re.I))
            .first
        )

    # --- навігація ---
    def open_page(self, path: str | None = None):
        self.page.goto(f"{settings.BASE_URL}{path or self.path}", wait_until="domcontentloaded")
        self.accept_cookies()
        return self

    def accept_cookies(self):
        """Закриває cookie-банер, якщо він з'явився."""
        try:
            self.page.get_by_role(
                "button", name=re.compile(r"^(accept|accept all|allow all)", re.I)
            ).first.click(timeout=2000)
        except Exception:
            pass

    def is_logged_in(self, timeout: int = 10000) -> bool:
        try:
            expect(self.account_menu_button).to_be_visible(timeout=timeout)
            return True
        except AssertionError:
            return False

    def logout(self):
        self.account_menu_button.click()
        self.page.get_by_text(re.compile(r"^log out$", re.I)).first.click()

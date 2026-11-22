import re

from playwright.sync_api import expect

from pages.base_page import BasePage


class BoardPage(BasePage):
    path = "/"

    @property
    def dialog(self):
        return self.page.get_by_role("dialog", name=re.compile(r"create a board", re.I))

    @property
    def name_input(self):
        return self.dialog.get_by_role("textbox", name="Board name")

    @property
    def private_checkbox(self):
        return self.dialog.get_by_role(
            "checkbox", name=re.compile(r"make this board private", re.I)
        )

    @property
    def create_button(self):
        return self.dialog.get_by_role("button", name="Create", exact=True)

    def open_create_dialog(self):
        self.open_page("/")
        self.page.get_by_role("button", name=re.compile(r"^create$", re.I)).first.click()
        self.page.get_by_text(re.compile(r"^board$", re.I)).first.click()
        expect(self.dialog).to_be_visible()
        return self

    def create_board(self, name: str, secret: bool = False):
        """secret=True вмикає чекбокс «Make this board private»."""
        self.open_create_dialog()
        self.name_input.fill(name)
        if secret:
            self.private_checkbox.check()
        expect(self.create_button).to_be_enabled()
        self.create_button.click()
        expect(self.dialog).to_be_hidden(timeout=15000)
        return self

    def board_title(self, name: str):
        return self.page.get_by_role("heading", name=name).first

    @property
    def secret_indicator(self):
        """Іконка замка або позначка приватної дошки на сторінці дошки."""
        main = self.page.get_by_role("main")
        return (
            main.locator('[aria-label*="private" i], [aria-label*="secret" i]')
            .or_(main.get_by_role("img", name=re.compile(r"private|secret", re.I)))
            .first
        )

    def delete_board(self, name: str):
        """Видаляє дошку лише якщо відкрита саме дошка з очікуваною назвою."""
        if self.board_title(name).count() == 0:
            return
        self.page.get_by_role("button", name=re.compile(r"edit board", re.I)).first.click()
        self.page.get_by_role("button", name=re.compile(r"^delete", re.I)).first.click()
        self.page.get_by_role("button", name=re.compile(r"^delete", re.I)).last.click()

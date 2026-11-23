import re
from pathlib import Path

from playwright.sync_api import expect

from pages.base_page import BasePage


class PinBuilderPage(BasePage):
    path = "/pin-creation-tool/"

    @property
    def file_input(self):
        return self.page.locator('input[type="file"]').first

    @property
    def title_input(self):
        return self.page.get_by_role("textbox", name="Title", exact=True)

    @property
    def description_input(self):
        return self.page.get_by_role("combobox", name=re.compile(r"describe your pin", re.I))

    @property
    def link_input(self):
        return self.page.get_by_role("textbox", name="Link", exact=True)

    @property
    def board_button(self):
        return self.page.get_by_role("button", name=re.compile(r"^board\b", re.I))

    @property
    def publish_button(self):
        return self.page.get_by_role("button", name=re.compile(r"^publish$", re.I))

    @property
    def success_toast(self):
        return self.page.get_by_text(re.compile(r"published|your pin|saved to", re.I)).first

    def dismiss_popups(self):
        """Закриває підказку «Got it», яка перекриває форму."""
        try:
            self.page.get_by_role("button", name="Got it").click(timeout=2000)
        except Exception:
            pass

    def choose_board(self, board_name: str):
        self.board_button.click()
        self.page.wait_for_timeout(1000)
        search = self.page.get_by_role("textbox", name=re.compile(r"search", re.I)).last
        try:
            if search.is_visible():
                search.fill(board_name)
                self.page.wait_for_timeout(800)
        except Exception:
            pass
        exact = re.compile(rf"^\s*{re.escape(board_name)}\s*$", re.I)
        option = self.page.get_by_role("option", name=re.compile(re.escape(board_name), re.I)).first
        candidates = [
            option,
            self.page.get_by_role("listitem").filter(has_text=exact).first,
            self.page.get_by_text(exact).first,
            self.page.get_by_role("button", name=re.compile(rf"^{re.escape(board_name)}\b", re.I)).first,
        ]
        for candidate in candidates:
            try:
                candidate.click(timeout=4000)
                return
            except Exception:
                continue
        visible = self.page.locator("body").inner_text()[:600].replace("\n", " | ")
        raise AssertionError(
            f"Дошку {board_name!r} не знайдено у списку. Перевір PINTEREST_BOARD у .env "
            f"(дошка має існувати в акаунті). Текст сторінки: {visible}"
        )

    def create_pin(self, image: Path, title: str, description: str, link: str, board: str):
        self.file_input.set_input_files(str(image))
        expect(self.title_input).to_be_visible()
        self.dismiss_popups()
        self.title_input.fill(title)
        self.description_input.click()
        self.description_input.fill(description)
        self.link_input.fill(link)
        self.choose_board(board)
        expect(self.publish_button).to_be_enabled()
        self.publish_button.click()
        return self

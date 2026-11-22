import re

from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.components.pin_grid import PinGrid


class HomePage(BasePage):
    path = "/"

    def __init__(self, page):
        super().__init__(page)
        self.grid = PinGrid(page)

    @property
    def pins(self):
        return self.grid.cards

    @property
    def board_chooser(self):
        return self.page.get_by_role("dialog").filter(
            has=self.page.get_by_role("heading", name="Save", exact=True)
        )

    @property
    def saved_confirmation(self):
        return self.page.get_by_text(re.compile(r"^saved( to)?", re.I)).first

    def save_first_pin(self, board_name: str = ""):
        """Репін першого піна. Якщо Pinterest просить обрати дошку, обирає board_name,
        а без назви першу в списку."""
        self.grid.save_first()
        try:
            expect(self.board_chooser).to_be_visible(timeout=3000)
        except AssertionError:
            return self  # пін збережено одразу на останню використану дошку
        if board_name:
            target = self.board_chooser.get_by_role(
                "button", name=re.compile(rf"^{re.escape(board_name)}\b", re.I)
            ).first
        else:
            target = self.board_chooser.get_by_role("listitem").first
        target.click()
        return self

import re

from playwright.sync_api import Page, expect


class PinGrid:
    """Сітка пінів: спільна для головної та сторінки результатів пошуку."""

    def __init__(self, page: Page):
        self.page = page

    @property
    def cards(self):
        return self.page.get_by_role("group", name=re.compile(r"^pin card$", re.I))

    def wait_loaded(self):
        expect(self.cards.first).to_be_visible()

    def save_first(self):
        """Репін першого піна (кнопка Save з'являється при наведенні)."""
        self.wait_loaded()
        self.page.wait_for_timeout(1500)  # дати стрічці дорендеритись, інакше картка «від'єднується»
        last_error = None
        for _ in range(5):
            try:
                card = self.cards.first
                card.scroll_into_view_if_needed(timeout=3000)
                card.hover(timeout=3000)
                card.get_by_role("button", name=re.compile(r"^save$", re.I)).click(timeout=3000)
                return
            except Exception as error:  # DOM перемальовано, пробуємо ще раз із новим локатором
                last_error = error
                self.page.wait_for_timeout(700)
        raise AssertionError(f"Не вдалося натиснути Save на першому піні: {last_error}")

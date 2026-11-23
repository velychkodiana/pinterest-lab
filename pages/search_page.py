import re

from pages.base_page import BasePage
from pages.components.pin_grid import PinGrid


class SearchPage(BasePage):
    path = "/"

    def __init__(self, page):
        super().__init__(page)
        self.grid = PinGrid(page)

    @property
    def pins(self):
        return self.grid.cards

    @property
    def suggestions(self):
        return self.page.get_by_role("option").or_(
            self.page.locator('[role="listbox"] [role="listitem"], [data-test-id*="typeahead" i] *')
        )

    @property
    def no_results_message(self):
        return self.page.get_by_text(
            re.compile(r"couldn.t find|no (pins|results|ideas) found|didn.t find any", re.I)
        ).first

    @property
    def fallback_results_message(self):
        return self.page.get_by_text(re.compile(r"showing more search results for", re.I)).first

    def search(self, query: str):
        self.search_input.click()
        self.search_input.fill(query)
        self.search_input.press("Enter")
        self.page.wait_for_url(re.compile(r"/search/"))
        return self

    def type_query(self, text: str):
        """Посимвольне введення для виклику автозаповнення."""
        self.search_input.click()
        self.search_input.press_sequentially(text, delay=80)
        return self

    def wait_for_results(self):
        self.grid.wait_loaded()

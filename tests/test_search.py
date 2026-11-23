import re

import pytest
from playwright.sync_api import expect

from pages.search_page import SearchPage

pytestmark = pytest.mark.search


@pytest.mark.parametrize("path", ["/", "/settings/", "/ideas/"])
def test_tc11_search_field_is_available_on_pages(auth_page, path):
    """TC-11 | FR-10 | Поле пошуку доступне на різних сторінках."""
    search = SearchPage(auth_page).open_page(path)
    expect(search.search_input).to_be_visible()


@pytest.mark.smoke
def test_tc12_search_by_relevant_query(auth_page):
    """TC-12 | FR-11 | Пошук за запитом «Design» повертає піни."""
    search = SearchPage(auth_page).open_page("/")
    search.search("Design")
    assert re.search(r"q=design", auth_page.url, re.I)
    search.wait_for_results()
    assert search.pins.count() > 0


def test_tc13_autocomplete_suggestions(auth_page):
    """TC-13 | FR-12 | Підказки автозаповнення для «Archite»."""
    search = SearchPage(auth_page).open_page("/")
    search.type_query("Archite")
    expect(
        search.suggestions.filter(has_text=re.compile("architecture", re.I)).first
    ).to_be_visible(timeout=10000)


@pytest.mark.negative
@pytest.mark.xfail(
    reason="Для запиту xyz123abc987 Pinterest не показує «нічого не знайдено», а повертає "
           "схожі піни («Showing more search results for ...»). Розбіжність з FR-14.",
    strict=False,
)
def test_tc15_search_without_results_shows_not_found_message(auth_page):
    """TC-15 | FR-14 | Очікування кейсу: повідомлення про відсутність результатів."""
    search = SearchPage(auth_page).open_page("/")
    search.search("xyz123abc987")
    expect(search.no_results_message).to_be_visible(timeout=5000)


@pytest.mark.negative
def test_tc15b_nonsense_query_does_not_break_application(auth_page):
    """TC-15 | FR-14 | Застосунок коректно обробляє безглуздий запит без системних помилок."""
    search = SearchPage(auth_page).open_page("/")
    search.search("xyz123abc987")
    expect(search.fallback_results_message.or_(search.no_results_message)).to_be_visible()
    expect(search.search_input).to_be_visible()
    expect(search.search_input).to_have_value("xyz123abc987")

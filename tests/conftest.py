import pytest

from config import settings
from pages.base_page import BasePage


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Англійська локаль, щоб тексти інтерфейсу збігалися з тест-кейсами."""
    return {
        **browser_context_args,
        "locale": "en-US",
        "viewport": {"width": 1440, "height": 900},
    }


def pytest_collection_modifyitems(items):
    """Порядок: тести на збережених сесіях -> вихід (TC-10) -> автоматичні входи (TC-07, TC-08).
    Входи йдуть останніми, бо їх може заблокувати Pinterest."""
    def rank(item):
        if item.name.startswith("test_tc10_logout"):
            return 1
        if item.name.startswith(("test_tc07_", "test_tc08_")):
            return 2
        return 0

    items.sort(key=rank)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    setattr(item, f"rep_{call.when}", outcome.get_result())


def _live_session_file(browser, context_args, filename: str) -> str:
    """Повертає файл сесії, якщо вона жива. Автоматичного входу тут немає."""
    state_file = settings.AUTH_DIR / filename
    if state_file.exists():
        context = browser.new_context(**context_args, storage_state=str(state_file))
        try:
            page = context.new_page()
            if BasePage(page).open_page("/").is_logged_in(timeout=8000):
                return str(state_file)
        finally:
            context.close()
    pytest.fail(
        f"Немає живої сесії ({filename}). Створи її вручну: "
        f"python save_auth.py {browser.browser_type.name}",
        pytrace=False,
    )


@pytest.fixture(scope="session")
def auth_state(browser, browser_context_args):
    return _live_session_file(browser, browser_context_args, f"state_{browser.browser_type.name}.json")


@pytest.fixture(scope="session")
def logout_state(browser, browser_context_args):
    return _live_session_file(
        browser, browser_context_args, f"state_{browser.browser_type.name}_logout.json"
    )


@pytest.fixture
def auth_page(browser, browser_context_args, auth_state, request):
    """Сторінка з уже авторизованою сесією."""
    context = browser.new_context(**browser_context_args, storage_state=auth_state)
    page = context.new_page()
    yield page
    rep = getattr(request.node, "rep_call", None)
    if rep is not None and rep.failed:
        settings.REPORTS_DIR.mkdir(exist_ok=True)
        page.screenshot(path=str(settings.REPORTS_DIR / f"FAIL_{request.node.name}.png"))
    context.close()

import pytest
from playwright.sync_api import expect

from config import settings
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.signup_page import SignupPage

pytestmark = pytest.mark.auth

requires_credentials = pytest.mark.skipif(
    not settings.HAS_CREDENTIALS, reason="Немає облікових даних у .env"
)

STRONG_PASSWORD = "Str0ng!Pass-2026"


@requires_credentials
@pytest.mark.smoke
def test_tc07_login_with_valid_credentials(page):
    """TC-07 | FR-6 | Вхід із валідними даними (Happy Path)."""
    login = LoginPage(page).open_page()
    login.login(settings.EMAIL, settings.PASSWORD)
    login.wait_until_logged_in()
    assert login.is_logged_in()


@requires_credentials
@pytest.mark.negative
def test_tc08_login_with_wrong_password(page):
    """TC-08 | FR-7 | Невірний пароль: вхід заблоковано, повідомлення не розкриває поле."""
    login = LoginPage(page).open_page()
    login.login(settings.EMAIL, "Wr0ng-Passw0rd!")
    try:
        expect(login.error_message).to_be_visible(timeout=15000)
    except AssertionError:
        if login.page.locator("dialog iframe, [role=\"dialog\"] iframe, iframe[src*=\"captcha\" i]").count():
            pytest.skip("Pinterest показав перевірку безпеки (CAPTCHA) замість помилки: "
                        "реалізація ризику «CAPTCHA/блокування» з тест-плану")
        raise
    assert not login.is_logged_in(timeout=2000)

    message = login.error_message.inner_text().strip()
    leaks = ("password you entered", "email you entered", "find an account")
    assert not any(phrase in message.lower() for phrase in leaks), (
        f"Повідомлення розкриває конкретне поле: {message!r}"
    )


@pytest.mark.smoke
def test_tc10_logout(browser, browser_context_args, logout_state):
    """TC-10 | FR-9 | Вихід із системи. Окрема сесія, яка після виходу стає недійсною."""
    context = browser.new_context(**browser_context_args, storage_state=logout_state)
    try:
        page = context.new_page()
        home = HomePage(page).open_page("/")
        assert home.is_logged_in()
        home.logout()
        expect(page.get_by_role("button", name="Log in").first).to_be_visible()
        assert not home.is_logged_in(timeout=2000)
    finally:
        context.close()


@pytest.mark.negative
@pytest.mark.parametrize("bad_email", ["test@.com", "test.com", "@mail.com", "test@@mail.com"])
def test_tc03_signup_rejects_invalid_email_format(page, bad_email):
    """TC-03 | FR-3 | Невалідний формат email (без створення акаунта).
    Без дати народження Continue не створює акаунт."""
    signup = SignupPage(page).open_form()
    signup.fill_credentials(bad_email, STRONG_PASSWORD)
    signup.blur()
    try:
        expect(signup.email_error).to_be_visible(timeout=3000)
    except AssertionError:
        signup.continue_button.click()
        expect(signup.email_error).to_be_visible(timeout=10000)


def test_tc05_password_strength_indicator_is_shown(page):
    """TC-05 | FR-4 | Індикатор надійності пароля відображається."""
    signup = SignupPage(page).open_form()
    signup.fill_credentials("qa.indicator.check@gmail.com", "1")
    expect(signup.password_meter).to_be_visible()


@pytest.mark.boundary
@pytest.mark.parametrize(
    "password, rejected",
    [
        ("1", True),
        ("12345", True),
        (STRONG_PASSWORD, False),
    ],
)
def test_tc04_signup_password_rules(page, password, rejected):
    """TC-04 | FR-4 | Слабкі паролі відхиляються, надійний приймається.
    Увага: Pinterest перевіряє надійність, а не довжину в 6 символів."""
    signup = SignupPage(page).open_form()
    signup.fill_credentials("qa.boundary.check@gmail.com", password)
    signup.blur()
    expect(signup.password_meter).to_be_visible()  # поле оброблено, тест не порожній
    if rejected:
        expect(signup.password_error).to_be_visible()
    else:
        expect(signup.password_error).to_have_count(0)

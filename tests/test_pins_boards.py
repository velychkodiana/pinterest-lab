import pytest
from playwright.sync_api import expect

from config import settings
from pages.board_page import BoardPage
from pages.home_page import HomePage
from pages.pin_builder_page import PinBuilderPage
from utils.helpers import make_test_image, unique_name

pytestmark = pytest.mark.pins


@pytest.mark.smoke
def test_tc19_repin_existing_pin(auth_page):
    """TC-19 | FR-18 | Збереження (репін) піна на дошку.
    Передумова: у тестового акаунта є принаймні одна дошка."""
    home = HomePage(auth_page).open_page("/")
    home.save_first_pin(board_name=settings.BOARD_NAME)
    expect(home.saved_confirmation).to_be_visible(timeout=10000)


@pytest.mark.smoke
@pytest.mark.skipif(not settings.BOARD_NAME, reason="Не задано PINTEREST_BOARD у .env")
def test_tc18_create_new_pin(auth_page, tmp_path):
    """TC-18 | FR-17 | Створення нового піна (зображення, назва, опис, посилання)."""
    image = make_test_image(tmp_path / "qa_pin.png")
    title = unique_name("qa-pin")
    builder = PinBuilderPage(auth_page).open_page()
    builder.create_pin(
        image=image,
        title=title,
        description="Автотест pinterest-qa-lab",
        link="https://example.com",
        board=settings.BOARD_NAME,
    )
    expect(builder.success_toast).to_be_visible()


@pytest.fixture
def created_boards(auth_page):
    """Збирає назви створених дошок і прибирає їх після тесту."""
    names = []
    yield names
    board = BoardPage(auth_page)
    for name in names:
        try:
            board.delete_board(name)
        except Exception as exc:
            print(f"\n[cleanup] Не вдалося видалити дошку {name}: {exc!r}")


def test_tc20_create_public_board(auth_page, created_boards):
    """TC-20 | FR-19 | Створення публічної дошки."""
    name = unique_name("qa-public")
    created_boards.append(name)
    board = BoardPage(auth_page)
    board.create_board(name, secret=False)
    expect(board.board_title(name)).to_be_visible(timeout=15000)
    expect(board.secret_indicator).to_have_count(0)


def test_tc21_create_secret_board(auth_page, created_boards):
    """TC-21 | FR-19 | Створення приватної дошки (іконка замка)."""
    name = unique_name("qa-secret")
    created_boards.append(name)
    board = BoardPage(auth_page)
    board.create_board(name, secret=True)
    expect(board.board_title(name)).to_be_visible(timeout=15000)
    expect(board.secret_indicator).to_be_visible()

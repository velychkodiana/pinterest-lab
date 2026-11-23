"""Створює збережені сесії входу вручну (без автоматичного входу, який блокує Pinterest).

Використання (кожну команду запускай окремо, без коментарів у рядку):
    python save_auth.py chromium            # обидві сесії: основна й для тесту виходу
    python save_auth.py chromium logout     # лише сесія для тесту виходу (після кожного повного прогону)
    python save_auth.py chromium main       # лише основна сесія
    python save_auth.py webkit              # те саме для WebKit
"""
import sys

from playwright.sync_api import sync_playwright

from config import settings

BROWSERS = {"chromium", "webkit"}
KINDS = {"all", "main", "logout"}


def main():
    browser_name = sys.argv[1] if len(sys.argv) > 1 else "chromium"
    kind = sys.argv[2] if len(sys.argv) > 2 else "all"
    if browser_name not in BROWSERS:
        sys.exit(f"Невідомий браузер. Доступні: {', '.join(sorted(BROWSERS))}")
    if kind not in KINDS:
        sys.exit(f"Невідомий тип сесії. Доступні: {', '.join(sorted(KINDS))}")

    settings.AUTH_DIR.mkdir(exist_ok=True)
    targets = {}
    if kind in ("all", "main"):
        targets["ОСНОВНА сесія"] = f"state_{browser_name}.json"
    if kind in ("all", "logout"):
        targets["сесія для тесту виходу TC-10"] = f"state_{browser_name}_logout.json"

    with sync_playwright() as p:
        browser = getattr(p, browser_name).launch(headless=False)
        for label, filename in targets.items():
            context = browser.new_context(locale="en-US", viewport={"width": 1440, "height": 900})
            page = context.new_page()
            page.goto(f"{settings.BASE_URL}/login/")
            input(f"[{label}] Увійди вручну, дочекайся головної сторінки й натисни Enter тут... ")
            context.storage_state(path=str(settings.AUTH_DIR / filename))
            context.close()
        browser.close()
    print(f"Готово: збережено сесій — {len(targets)}.")


if __name__ == "__main__":
    main()

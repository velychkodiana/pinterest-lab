"""Запускає всі тести ПО ЧЕРЗІ трьома етапами й готує окремий HTML-звіт для кожного.

Етапи:
  main    - усі тести на збережених сесіях (пошук, піни, дошки, форма реєстрації)
  logout  - TC-10 (вихід), використовує окрему сесію
  login   - TC-07 і TC-08 (автоматичний вхід; Pinterest може його блокувати)

Приклади:
    python run_all.py                              # усі три етапи по черзі
    python run_all.py --stages main                # лише основний етап
    python run_all.py --stages main,logout         # без автоматичних входів
    python run_all.py --browser webkit             # той самий набір у WebKit
    python run_all.py --headless                   # без вікна браузера
"""
import argparse
import subprocess
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

STAGES = {
    "main": 'not tc07 and not tc08 and not tc10',
    "logout": "tc10",
    "login": "tc07 or tc08",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stages", default="main,logout,login", help="через кому: main,logout,login")
    parser.add_argument("--browser", default="chromium", choices=["chromium", "webkit", "firefox"])
    parser.add_argument("--headless", action="store_true", help="не показувати вікно браузера")
    parser.add_argument("--no-open", action="store_true", help="не відкривати звіти в браузері")
    args = parser.parse_args()

    stages = [s.strip() for s in args.stages.split(",") if s.strip()]
    unknown = [s for s in stages if s not in STAGES]
    if unknown:
        sys.exit(f"Невідомі етапи: {unknown}. Доступні: {list(STAGES)}")

    reports = Path("reports")
    reports.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    summary = []
    for i, stage in enumerate(stages, 1):
        report = reports / f"{i}_{stage}_{args.browser}_{stamp}.html"
        cmd = [sys.executable, "-m", "pytest", "-k", STAGES[stage], "--browser", args.browser,
               f"--html={report}", "--self-contained-html"]
        if not args.headless:
            cmd.append("--headed")
        print(f"\n===== ЕТАП {i}/{len(stages)}: {stage} =====")
        code = subprocess.call(cmd)
        summary.append((stage, code, report))

    print("\n===== ПІДСУМОК =====")
    for stage, code, report in summary:
        status = "OK" if code == 0 else f"є помилки (код {code})"
        print(f"{stage:<8} {status:<22} {report.resolve().as_uri()}")
        if not args.no_open:
            webbrowser.open(report.resolve().as_uri())
    sys.exit(max(code for _, code, _ in summary))


if __name__ == "__main__":
    main()

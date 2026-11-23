from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw


def unique_name(prefix: str) -> str:
    """Унікальна назва для дошок/пінів, щоб тести не конфліктували."""
    return f"{prefix}-{datetime.now():%Y%m%d-%H%M%S}"


def make_test_image(path: Path, text: str = "QA") -> Path:
    """Генерує тестове зображення для завантаження піна."""
    img = Image.new("RGB", (800, 1000), color=(230, 0, 35))
    ImageDraw.Draw(img).text((380, 490), text, fill=(255, 255, 255))
    img.save(path, "PNG")
    return path

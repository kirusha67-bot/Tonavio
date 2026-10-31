
import os
import json
import asyncio
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

PORTALS_API_KEY = os.getenv("PORTALS_API_KEY")
PORTALS_BASE_URL = "https://portal-market.com/partners"


def _get_portals_data(endpoint: str):
    if not PORTALS_API_KEY:
        raise ValueError("PORTALS_API_KEY не найден")

    request = Request(
        f"{PORTALS_BASE_URL}{endpoint}",
        headers={
            "Authorization": f"partners {PORTALS_API_KEY}",
            "Accept": "application/json",
            "User-Agent": "Tonavio/0.1",
        },
        method="GET",
    )

    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    except HTTPError as error:
        response_body = error.read().decode(
            "utf-8",
            errors="replace"
        )

        print("PORTALS HTTP STATUS:", error.code)
        print("PORTALS SERVER:", error.headers.get("Server"))
        print("PORTALS RESPONSE:", response_body[:1000])

        raise RuntimeError(
            f"Portals API вернул HTTP-ошибку: {error.code}. "
            f"Ответ сервера: {response_body[:500]}"
        ) from None

    except URLError as error:
        raise RuntimeError(
            f"Не удалось подключиться к Portals API: {error.reason}"
        ) from None


async def collect_gifts():
    """Получает реальные данные о флорах Portals."""

    collection_floors = await asyncio.to_thread(
        _get_portals_data,
        "/collections/floors",
    )

    await asyncio.sleep(1.1)

    attribute_floors = await asyncio.to_thread(
        _get_portals_data,
        "/collections/attribute-floors",
    )

    return {
        "source": "Portals",
        "collection_floors": collection_floors,
        "attribute_floors": attribute_floors,
    }


import os
import json
import asyncio
import time
from urllib.parse import urlencode
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


_IMAGE_CACHE = {"expires": 0, "data": None}


def _normalized(value):
    return "".join(ch.lower() for ch in str(value or "") if ch.isalnum())


def _items(payload, *keys):
    current = payload
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return []
    return current if isinstance(current, list) else []


def _first_image(item):
    if not isinstance(item, dict):
        return None
    for key in ("photo_url", "image_url", "image", "thumbnail_url"):
        value = item.get(key)
        if isinstance(value, str) and value.startswith(("https://", "http://")):
            return value
    return None


async def collect_market_images():
    """Returns Portals preview images and representative NFT images per model."""
    now = time.time()
    if _IMAGE_CACHE["data"] and now < _IMAGE_CACHE["expires"]:
        return _IMAGE_CACHE["data"]

    floors_data = await collect_gifts()
    raw_models = floors_data.get("attribute_floors", {}).get("models", [])
    models = [m for m in raw_models if isinstance(m, dict)] if isinstance(raw_models, list) else []

    preview_payload = await asyncio.to_thread(_get_portals_data, "/collections/preview")
    preview_rows = preview_payload.get("collections", []) if isinstance(preview_payload, dict) else []
    preview_by_slug = {}
    preview_by_name = {}
    for item in preview_rows if isinstance(preview_rows, list) else []:
        if not isinstance(item, dict):
            continue
        if item.get("short_name"):
            preview_by_slug[_normalized(item["short_name"])] = item
        if item.get("name"):
            preview_by_name[_normalized(item["name"])] = item

    # Map each collection by either its actual API slug or its display name.
    collection_lookup = {}
    for slug in floors_data.get("collection_floors", {}).get("floorPrices", {}):
        item = preview_by_slug.get(_normalized(slug)) or preview_by_name.get(_normalized(slug.replace("-", " ").replace("_", " ")))
        if item:
            collection_lookup[_normalized(slug)] = item

    # Model floors contain the full collection display name. Resolve the preview UUID
    # through both preview name and short_name so NFT image queries use the right ID.
    groups = {}
    for model in models:
        collection_name = str(model.get("collection_name") or "")
        model_name = str(model.get("name") or "")
        if not collection_name or not model_name:
            continue
        key = _normalized(collection_name)
        groups.setdefault(key, {"collection_name": collection_name, "models": []})["models"].append(model_name)

    preview_for_group = {}
    for key, group in groups.items():
        preview_for_group[key] = preview_by_name.get(key)
        if not preview_for_group[key]:
            preview_for_group[key] = preview_by_slug.get(key)

    async def find_model_image(collection_id, model_name):
        params = [
            ("collection_id", str(collection_id)),
            ("filter_by_models", model_name),
            ("sort_by", "price desc"),
            ("limit", "1"),
        ]
        try:
            payload = await asyncio.to_thread(
                _get_portals_data,
                "/nfts/search?" + urlencode(params)
            )
            results = payload.get("results", []) if isinstance(payload, dict) else []
            if results and isinstance(results[0], dict):
                return _first_image(results[0])
        except Exception as error:
            print("PORTALS MODEL IMAGE:", model_name, str(error)[:180])
        return None

    # Ask for one representative NFT per model. Bounded concurrency avoids
    # overwhelming the partner API; images are cached for 30 minutes.
    semaphore = asyncio.Semaphore(4)
    async def guarded_lookup(collection_id, model_name):
        async with semaphore:
            return await find_model_image(collection_id, model_name)

    tasks = {}
    for key, group in groups.items():
        preview_item = preview_for_group.get(key)
        collection_id = preview_item.get("id") if isinstance(preview_item, dict) else None
        if not collection_id:
            continue
        for model_name in dict.fromkeys(group["models"]):
            tasks[(key, _normalized(model_name))] = asyncio.create_task(
                guarded_lookup(collection_id, model_name)
            )

    model_images = {}
    if tasks:
        values = await asyncio.gather(*tasks.values())
        model_images = {key: value for key, value in zip(tasks.keys(), values) if value}

    collection_rows = []
    for slug, floor in floors_data.get("collection_floors", {}).get("floorPrices", {}).items():
        preview_item = collection_lookup.get(_normalized(slug))
        group = groups.get(_normalized(preview_item.get("name"))) if preview_item else None
        if not group:
            group = groups.get(_normalized(slug))
        top_model = None
        if group:
            candidates = [m for m in models if _normalized(m.get("collection_name")) == _normalized(group["collection_name"])]
            if candidates:
                top_model = max(candidates, key=lambda x: float(x.get("floor_price") or 0))
        top_name = str(top_model.get("name")) if top_model else None
        model_photo = model_images.get((_normalized(group["collection_name"]), _normalized(top_name))) if group and top_name else None
        collection_photo = _first_image(preview_item) if preview_item else None
        collection_rows.append({
            "slug": slug,
            "photo_url": model_photo or collection_photo,
            "top_model": top_name,
            "image_source": "model" if model_photo else ("collection" if collection_photo else None)
        })

    model_rows = []
    for model in models:
        key = _normalized(model.get("collection_name"))
        model_rows.append({
            "collection_name": model.get("collection_name"),
            "name": model.get("name"),
            "photo_url": model_images.get((key, _normalized(model.get("name"))))
        })

    data = {"collections": collection_rows, "models": model_rows}
    _IMAGE_CACHE.update({"expires": now + 1800, "data": data})
    return data

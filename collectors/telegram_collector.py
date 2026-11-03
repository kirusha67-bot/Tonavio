
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
    """Returns cached Portals images for collections and their models."""
    now = time.time()
    if _IMAGE_CACHE["data"] and now < _IMAGE_CACHE["expires"]:
        return _IMAGE_CACHE["data"]

    floors_data = await collect_gifts()
    models = floors_data.get("attribute_floors", {}).get("models", [])
    if not isinstance(models, list):
        models = []

    preview = await asyncio.to_thread(_get_portals_data, "/collections/preview")
    collections = (
        preview.get("collections", [])
        if isinstance(preview, dict)
        else []
    )
    if not isinstance(collections, list) and isinstance(preview, dict):
        collections = preview.get("data", {}).get("collections", [])

    preview_by_name = {}
    for item in collections if isinstance(collections, list) else []:
        if isinstance(item, dict):
            key = _normalized(item.get("short_name") or item.get("name"))
            if key:
                preview_by_name[key] = item

    # Fetch one batch of the most expensive listed gifts per collection.
    # The returned NFT attributes let us map each actual image to its model.
    grouped = {}
    for model in models:
        if not isinstance(model, dict):
            continue
        collection_name = str(model.get("collection_name") or "")
        model_name = str(model.get("name") or "")
        if collection_name and model_name:
            grouped.setdefault(_normalized(collection_name), {
                "collection_name": collection_name,
                "models": []
            })["models"].append(model_name)

    model_images = {}
    collection_images = {}
    for key, group in grouped.items():
        preview_item = preview_by_name.get(key)
        collection_id = preview_item.get("id") if isinstance(preview_item, dict) else None
        if preview_item:
            collection_images[key] = _first_image(preview_item)

        if not collection_id:
            continue

        params = [("collection_id", str(collection_id)), ("sort_by", "price desc"), ("limit", "100"), ("status", "listed")]
        params.extend(("filter_by_models", name) for name in dict.fromkeys(group["models"]))
        endpoint = "/nfts/search?" + urlencode(params)
        try:
            result = await asyncio.to_thread(_get_portals_data, endpoint)
            nft_items = result.get("results", []) if isinstance(result, dict) else []
            if not isinstance(nft_items, list) and isinstance(result, dict):
                nft_items = result.get("data", {}).get("results", [])
            for nft in nft_items if isinstance(nft_items, list) else []:
                image_url = _first_image(nft)
                if not image_url:
                    continue
                attributes = nft.get("attributes", [])
                if isinstance(attributes, dict):
                    attributes = [{"type": k, "name": v} for k, v in attributes.items()]
                for attr in attributes if isinstance(attributes, list) else []:
                    if not isinstance(attr, dict):
                        continue
                    attr_name = str(attr.get("name") or attr.get("value") or "")
                    attr_type = str(attr.get("type") or attr.get("trait_type") or "").lower()
                    if attr_name and (not attr_type or "model" in attr_type):
                        model_images[(key, _normalized(attr_name))] = image_url
        except Exception as error:
            # Images are optional; floor data must remain available if this endpoint
            # is temporarily unavailable or the partner API limits the request.
            print("PORTALS IMAGE LOOKUP:", group["collection_name"], str(error)[:250])

    collection_rows = []
    for slug, floor in floors_data.get("collection_floors", {}).get("floorPrices", {}).items():
        name = slug
        preview_item = preview_by_name.get(_normalized(name)) or preview_by_name.get(_normalized(name.replace("-", " ").replace("_", " ")))
        group = grouped.get(_normalized(name)) or next(
            (v for k, v in grouped.items() if k == _normalized(name.replace("-", "").replace("_", ""))),
            None
        )
        top_model = None
        if group:
            candidates = [m for m in models if _normalized(m.get("collection_name")) == _normalized(group["collection_name"])]
            if candidates:
                top_model = max(candidates, key=lambda x: float(x.get("floor_price") or 0))
        top_name = str(top_model.get("name")) if top_model else None
        image = model_images.get((_normalized(group["collection_name"]), _normalized(top_name))) if group and top_name else None
        if not image and preview_item:
            image = _first_image(preview_item)
        collection_rows.append({
            "slug": slug,
            "photo_url": image,
            "top_model": top_name
        })

    model_rows = []
    for model in models:
        if not isinstance(model, dict):
            continue
        key = _normalized(model.get("collection_name"))
        model_rows.append({
            "collection_name": model.get("collection_name"),
            "name": model.get("name"),
            "photo_url": model_images.get((key, _normalized(model.get("name"))))
        })

    data = {"collections": collection_rows, "models": model_rows}
    _IMAGE_CACHE.update({"expires": now + 1800, "data": data})
    return data

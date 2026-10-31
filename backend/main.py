
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from collectors.telegram_collector import collect_gifts


app = FastAPI(title="Tonavio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kirusha67-bot.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Tonavio API"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


# Пока сохраняем старые тестовые данные,
# чтобы не нарушить работу существующего Mini App.
@app.get("/gifts")
async def gifts():
    return {
        "gifts": [
            {
                "name": "Plush Pepe",
                "number": 1842,
                "currency": "TON",
                "marketplaces": [
                    {"name": "Portals", "price": 18.4},
                    {"name": "MRKT", "price": 19.1},
                    {"name": "TONNEL", "price": 20.0}
                ]
            },
            {
                "name": "Heart Locket",
                "number": 529,
                "currency": "TON",
                "marketplaces": [
                    {"name": "Portals", "price": 13.4},
                    {"name": "MRKT", "price": 12.7},
                    {"name": "TONNEL", "price": 14.2}
                ]
            },
            {
                "name": "Scared Cat",
                "number": 9100,
                "currency": "TON",
                "marketplaces": [
                    {"name": "Portals", "price": 25.3},
                    {"name": "MRKT", "price": 26.0},
                    {"name": "TONNEL", "price": 24.1}
                ]
            }
        ]
    }


# Новый маршрут с реальными данными Portals
@app.get("/portals/floors")
async def portals_floors():
    try:
        data = await collect_gifts()

        return {
            "status": "ok",
            "data": data
        }

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Ошибка получения данных Portals: {error}"
        ) from error

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/gifts")
async def gifts():
    return {
        "gifts": [
            {
                "name": "Plush Pepe",
                "number": 1842,
                "price": 18.4,
                "currency": "TON",
                "marketplace": "Portals"
            },
            {
                "name": "Heart Locket",
                "number": 529,
                "price": 12.7,
                "currency": "TON",
                "marketplace": "MRKT"
            },
            {
                "name": "Scared Cat",
                "number": 9100,
                "price": 24.1,
                "currency": "TON",
                "marketplace": "TONNEL"
            }
        ]
    }
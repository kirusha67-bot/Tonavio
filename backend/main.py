from fastapi import FastAPI

app = FastAPI(title="Tonavio API")


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
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
import logging

import httpx
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from app.client import geocode_city
from app.logging_config import CorrelationIdMiddleware, setup_logging
from app.schemas import ErrorResponse, GeocodeResponse

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Geocode Service")
app.add_middleware(CorrelationIdMiddleware)


@app.get("/geocode", response_model=GeocodeResponse, responses={404: {"model": ErrorResponse}})
async def geocode(city: str = Query(..., min_length=1)) -> JSONResponse | GeocodeResponse:
    try:
        result = await geocode_city(city)
    except httpx.TimeoutException:
        logger.error("Upstream timeout while geocoding city=%s", city)
        return JSONResponse(status_code=502, content={"detail": "Upstream service timeout"})
    except httpx.HTTPStatusError as exc:
        logger.error("Upstream error status=%s city=%s", exc.response.status_code, city)
        return JSONResponse(status_code=502, content={"detail": "Upstream service error"})

    if result is None:
        return JSONResponse(status_code=404, content={"detail": f"City not found: {city}"})

    return result


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}

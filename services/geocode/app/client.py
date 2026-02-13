import httpx

from app.schemas import GeocodeResponse

OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


async def geocode_city(city: str) -> GeocodeResponse | None:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            OPEN_METEO_GEOCODING_URL,
            params={"name": city, "count": 1},
        )
        resp.raise_for_status()

    data = resp.json()
    results = data.get("results")
    if not results:
        return None

    hit = results[0]
    return GeocodeResponse(
        name=hit["name"],
        latitude=hit["latitude"],
        longitude=hit["longitude"],
    )

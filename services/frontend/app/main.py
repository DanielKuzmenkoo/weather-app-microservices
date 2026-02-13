import os
import uuid

import httpx
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Weather App Frontend")

_template_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=_template_dir)

GEOCODE_SERVICE_URL = os.environ.get("GEOCODE_SERVICE_URL", "http://localhost:8001")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", {"result": None, "error": None, "city": None})


@app.post("/search", response_class=HTMLResponse)
async def search(request: Request, city: str = Form(...)) -> HTMLResponse:
    correlation_id = str(uuid.uuid4())
    result = None
    error = None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{GEOCODE_SERVICE_URL}/geocode",
                params={"city": city},
                headers={"X-Correlation-ID": correlation_id},
            )

        if resp.status_code == 200:
            result = resp.json()
        elif resp.status_code == 404:
            error = resp.json().get("detail", "City not found")
        else:
            error = f"Geocode service error (HTTP {resp.status_code})"

    except httpx.TimeoutException:
        error = "Geocode service timed out. Please try again."
    except httpx.ConnectError:
        error = "Could not connect to the geocode service."

    return templates.TemplateResponse(
        request, "index.html", {"result": result, "error": error, "city": city}
    )

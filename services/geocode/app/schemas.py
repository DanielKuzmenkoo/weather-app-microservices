from pydantic import BaseModel


class GeocodeResponse(BaseModel):
    name: str
    latitude: float
    longitude: float


class ErrorResponse(BaseModel):
    detail: str

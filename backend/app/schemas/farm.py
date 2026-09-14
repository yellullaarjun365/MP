from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FarmCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    farm_type: str | None = Field(default=None, max_length=100)
    total_area_m2: float | None = Field(default=None, gt=0)
    water_source: str | None = Field(default=None, max_length=100)


class FarmUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    farm_type: str | None = Field(default=None, max_length=100)
    total_area_m2: float | None = Field(default=None, gt=0)
    water_source: str | None = Field(default=None, max_length=100)


class FarmRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    name: str
    location: str | None
    farm_type: str | None
    total_area_m2: float | None
    water_source: str | None

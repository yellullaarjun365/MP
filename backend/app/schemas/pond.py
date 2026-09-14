from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PondCreate(BaseModel):
    farm_id: UUID
    name: str = Field(min_length=1, max_length=255)
    species_id: UUID | None = None
    area_m2: float | None = Field(default=None, gt=0)
    depth_m: float | None = Field(default=None, gt=0)
    culture_type: str | None = Field(default=None, max_length=100)
    water_source: str | None = Field(default=None, max_length=100)


class PondUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    species_id: UUID | None = None
    area_m2: float | None = Field(default=None, gt=0)
    depth_m: float | None = Field(default=None, gt=0)
    culture_type: str | None = Field(default=None, max_length=100)
    water_source: str | None = Field(default=None, max_length=100)


class PondRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    farm_id: UUID
    species_id: UUID | None
    name: str
    area_m2: float | None
    depth_m: float | None
    culture_type: str | None
    water_source: str | None

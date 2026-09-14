from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# REQUEST SCHEMAS
# ============================================================

class OnboardingFarmCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    farm_type: str | None = Field(default=None, max_length=100)
    total_area_m2: float | None = Field(default=None, gt=0)
    water_source: str | None = Field(default=None, max_length=100)


class OnboardingPondCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    species_id: UUID
    area_m2: float | None = Field(default=None, gt=0)
    depth_m: float | None = Field(default=None, gt=0)
    culture_type: str | None = Field(default=None, max_length=100)
    water_source: str | None = Field(default=None, max_length=100)


class OnboardingSetupCreate(BaseModel):
    farm: OnboardingFarmCreate

    ponds: list[OnboardingPondCreate] = Field(
        min_length=1,
        max_length=100,
    )


# ============================================================
# RESPONSE SCHEMAS
# ============================================================

class OnboardingSpeciesRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    common_name: str
    scientific_name: str | None
    category: str | None
    is_active: bool


class OnboardingPondRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    farm_id: UUID
    species_id: UUID | None
    name: str
    area_m2: float | None
    depth_m: float | None
    culture_type: str | None
    water_source: str | None
    species: OnboardingSpeciesRead | None


class OnboardingFarmRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    name: str
    location: str | None
    farm_type: str | None
    total_area_m2: float | None
    water_source: str | None
    ponds: list[OnboardingPondRead]

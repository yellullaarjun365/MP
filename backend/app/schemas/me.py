from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MeFarmRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    location: str | None
    farm_type: str | None
    total_area_m2: float | None
    water_source: str | None


class MeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str | None
    onboarding_status: str
    farms: list[MeFarmRead]
    farm_count: int

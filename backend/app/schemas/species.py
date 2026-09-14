from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SpeciesCreate(BaseModel):
    common_name: str = Field(min_length=1, max_length=255)
    scientific_name: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=100)


class SpeciesUpdate(BaseModel):
    common_name: str | None = Field(default=None, min_length=1, max_length=255)
    scientific_name: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None


class SpeciesRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    common_name: str
    scientific_name: str | None
    category: str | None
    is_active: bool

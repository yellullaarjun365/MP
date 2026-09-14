from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WaterQualityCreate(BaseModel):
    pond_id: UUID
    parameter: str = Field(min_length=1, max_length=100)
    value: float
    unit: str = Field(min_length=1, max_length=50)
    measured_at: datetime
    source: str = Field(default="manual", min_length=1, max_length=50)


class WaterQualityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pond_id: UUID
    parameter: str
    value: float
    unit: str
    measured_at: datetime
    source: str


class FeedingCreate(BaseModel):
    pond_id: UUID
    feed_type: str = Field(min_length=1, max_length=100)
    quantity_kg: float = Field(gt=0)
    fed_at: datetime
    source: str = Field(default="manual", min_length=1, max_length=50)


class FeedingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pond_id: UUID
    feed_type: str
    quantity_kg: float
    fed_at: datetime
    source: str


class StockingCreate(BaseModel):
    pond_id: UUID
    species_id: UUID
    stocked_at: datetime
    quantity: float = Field(gt=0)
    initial_average_weight_g: float | None = Field(default=None, gt=0)
    source: str = Field(default="manual", min_length=1, max_length=100)


class StockingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pond_id: UUID
    species_id: UUID
    stocked_at: datetime
    quantity: float
    initial_average_weight_g: float | None
    source: str


class GrowthCreate(BaseModel):
    pond_id: UUID
    sampled_at: datetime
    average_weight_g: float = Field(gt=0)
    sample_size: int = Field(gt=0)
    estimated_biomass_kg: float | None = Field(default=None, gt=0)
    source: str = Field(default="manual", min_length=1, max_length=50)


class GrowthRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pond_id: UUID
    sampled_at: datetime
    average_weight_g: float
    sample_size: int
    estimated_biomass_kg: float | None
    source: str


class HealthCreate(BaseModel):
    pond_id: UUID
    observed_at: datetime
    event_type: str = Field(min_length=1, max_length=100)
    mortality_count: int | None = Field(default=None, ge=0)
    symptoms: str | None = None
    treatment: str | None = None
    notes: str | None = None
    source: str = Field(default="manual", min_length=1, max_length=50)


class HealthRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pond_id: UUID
    observed_at: datetime
    event_type: str
    mortality_count: int | None
    symptoms: str | None
    treatment: str | None
    notes: str | None
    source: str


class HarvestCreate(BaseModel):
    pond_id: UUID
    harvested_at: datetime
    quantity_kg: float = Field(gt=0)
    average_weight_g: float | None = Field(default=None, gt=0)
    survival_rate: float | None = Field(default=None, ge=0, le=100)
    selling_price_per_kg: float | None = Field(default=None, ge=0)
    buyer: str | None = Field(default=None, max_length=255)
    source: str = Field(default="manual", min_length=1, max_length=50)
    notes: str | None = None


class HarvestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pond_id: UUID
    harvested_at: datetime
    quantity_kg: float
    average_weight_g: float | None
    survival_rate: float | None
    selling_price_per_kg: float | None
    buyer: str | None
    source: str
    notes: str | None

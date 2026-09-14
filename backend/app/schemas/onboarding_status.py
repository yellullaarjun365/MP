from pydantic import BaseModel


class OnboardingStatusRead(BaseModel):
    status: str
    farm_count: int
    needs_setup: bool

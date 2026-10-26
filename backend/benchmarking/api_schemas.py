from pydantic import BaseModel, Field


class BenchmarkStartRequest(BaseModel):
    name: str = Field(default="Model comparison", min_length=1, max_length=120)
    models: list[str] = Field(min_length=1, max_length=4)
    scenario_ids: list[str] = Field(default_factory=list, max_length=30)
    prompt_modes: list[str] = Field(default_factory=lambda: ["baseline", "optimized"])
    repetitions: int = Field(default=3, ge=1, le=20)


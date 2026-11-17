from dataclasses import dataclass

@dataclass(slots=True)
class Embedding:
    chunk_id: str
    vector: list[float]
    model_name: str
    dimension: int
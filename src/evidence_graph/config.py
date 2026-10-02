from dataclasses import dataclass, field
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class ModelConfig:
    name: str = "qwen3:8b"
    provider: str = "ollama"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.0


@dataclass
class BenchmarkConfig:
    runner: str = "default"
    save_results: bool = True

    results_dir: Path = PROJECT_ROOT / "experiments" / "results"


@dataclass
class AppConfig:
    data_dir: Path = PROJECT_ROOT / "data"

    papers_dir: Path = field(init=False)
    parsed_dir: Path = field(init=False)

    model: ModelConfig = field(default_factory=ModelConfig)
    benchmark: BenchmarkConfig = field(default_factory=BenchmarkConfig)

    def __post_init__(self):
        self.papers_dir = self.data_dir / "papers"
        self.parsed_dir = self.data_dir / "parsed"
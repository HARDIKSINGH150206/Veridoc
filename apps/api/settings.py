"""The one settings module. All configuration comes from here.

Values are read from environment variables (prefix VERIDOC_) and from a local .env file.
Nothing else in the code base may hold a path, port, URL, key or model name.
Meanings of each setting: docs/ARCHITECTURE.md section 12. Names only are listed in .env.example.
"""

from pathlib import Path
from typing import Annotated, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="VERIDOC_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    # The API only ever listens on the loopback interface (NFR-SEC-004).
    host: Literal["127.0.0.1"] = "127.0.0.1"
    port: int | None = None

    home: Path | None = None
    model_dir: Path | None = None
    manifest_path: Path | None = None
    max_import_mb: int | None = None
    log_level: str = "INFO"

    # Hardware tiers: minimum RAM in GB for each tier. Values are tuned by benchmark (Q-35).
    tier: Literal["high", "default", "low", "safe"] | None = None
    tier_high_min_ram_gb: int = 16
    tier_default_min_ram_gb: int = 8
    tier_low_min_ram_gb: int = 4

    safe_mode: bool = False
    # Demo mode switches stubs and fixtures on. It is a setting, never a code edit.
    demo_mode: bool = False
    feature_flags: Annotated[list[str], NoDecode] = []

    # P1 only, off by default.
    anchor_enabled: bool = False
    anchor_rpc: str | None = None
    share_base_url: str | None = None

    @field_validator("feature_flags", mode="before")
    @classmethod
    def split_flags(cls, value: object) -> object:
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

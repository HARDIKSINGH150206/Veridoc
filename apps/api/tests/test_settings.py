"""Tests for apps/api/settings.py (written before the module)."""

from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from apps.api.settings import Settings


def load(env_file: Path | None) -> Settings:
    # pydantic-settings accepts _env_file at runtime; mypy does not know that.
    kwargs: dict[str, Any] = {"_env_file": env_file}
    return Settings(**kwargs)


def make(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, **env: str) -> Settings:
    monkeypatch.chdir(tmp_path)  # no stray .env
    for key in list(__import__("os").environ):
        if key.startswith("VERIDOC_"):
            monkeypatch.delenv(key)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return load(None)


def test_defaults_do_not_enable_optional_features(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    s = make(monkeypatch, tmp_path)
    assert s.safe_mode is False
    assert s.demo_mode is False
    assert s.anchor_enabled is False
    assert s.feature_flags == []
    assert s.port is None
    assert s.home is None


def test_reads_environment_variables(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    s = make(
        monkeypatch,
        tmp_path,
        VERIDOC_PORT="9100",
        VERIDOC_SAFE_MODE="1",
        VERIDOC_DEMO_MODE="true",
        VERIDOC_MAX_IMPORT_MB="25",
        VERIDOC_FEATURE_FLAGS="blind_handshake, use_fixtures",
        VERIDOC_HOME=str(tmp_path / "vault"),
    )
    assert s.port == 9100
    assert s.safe_mode is True
    assert s.demo_mode is True
    assert s.max_import_mb == 25
    assert s.feature_flags == ["blind_handshake", "use_fixtures"]
    assert s.home == tmp_path / "vault"


def test_empty_values_in_env_file_mean_unset(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_text("VERIDOC_PORT=\nVERIDOC_SAFE_MODE=\nVERIDOC_FEATURE_FLAGS=\n")
    s = load(env_file)
    assert s.port is None
    assert s.safe_mode is False
    assert s.feature_flags == []


def test_env_file_is_read(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    for key in list(__import__("os").environ):
        if key.startswith("VERIDOC_"):
            monkeypatch.delenv(key)
    env_file = tmp_path / ".env"
    env_file.write_text("VERIDOC_LOG_LEVEL=DEBUG\n")
    assert load(env_file).log_level == "DEBUG"


def test_bad_values_are_rejected(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        make(monkeypatch, tmp_path, VERIDOC_PORT="not-a-number")


def test_tier_thresholds_are_configuration(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    s = make(monkeypatch, tmp_path, VERIDOC_TIER_HIGH_MIN_RAM_GB="32")
    assert s.tier_high_min_ram_gb == 32
    assert s.tier_default_min_ram_gb < s.tier_high_min_ram_gb
    assert s.tier_low_min_ram_gb < s.tier_default_min_ram_gb

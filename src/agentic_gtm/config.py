"""Workspace configuration and environment boundaries."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field


class Policies(BaseModel):
    model_config = ConfigDict(extra="forbid")
    external_writes: str = "plan_then_apply"
    campaigns_must_remain_paused: bool = True
    require_supabase_for_connected_workflows: bool = False


class StoreSettings(BaseModel):
    """Where operational records live.

    `supabase` is the default and the recommended choice for any team. `files`
    keeps CSV tables and JSON plans under `path` for a first experiment without
    a database. `auto` uses Supabase when its credentials are present and falls
    back to files otherwise, printing which backend is active.
    """

    model_config = ConfigDict(extra="forbid")
    backend: Literal["auto", "supabase", "files"] = "auto"
    path: str = ".gtm/store"


class Settings(BaseModel):
    model_config = ConfigDict(extra="allow")
    version: int = 1
    company: dict[str, Any] = Field(default_factory=dict)
    providers: dict[str, str] = Field(default_factory=dict)
    policies: Policies = Field(default_factory=Policies)
    store: StoreSettings = Field(default_factory=StoreSettings)
    scopes: dict[str, Any] = Field(default_factory=dict)
    field_maps: dict[str, dict[str, str]] = Field(default_factory=dict)
    artifacts: dict[str, str] = Field(default_factory=lambda: {"root": "."})


def load_settings(path: Path | str = "gtm.yaml") -> Settings:
    load_dotenv(override=False)
    config_path = Path(path)
    if not config_path.exists():
        return Settings()
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return Settings.model_validate(data)


def credential(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing {name}. Add it to .env; credentials are never CLI arguments.")
    return value


def has_supabase() -> bool:
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

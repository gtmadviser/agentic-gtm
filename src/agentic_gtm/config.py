"""Workspace configuration and environment boundaries."""

from __future__ import annotations

import os
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Literal

import yaml
from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict, Field


class Policies(BaseModel):
    model_config = ConfigDict(extra="forbid")
    external_writes: Literal["plan_then_apply"] = "plan_then_apply"
    campaigns_must_remain_paused: Literal[True] = True
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
    workspace_root: Path = Field(default_factory=Path.cwd, exclude=True)

    def resolve(self, path: Path | str) -> Path:
        candidate = Path(path).expanduser()
        return (
            candidate.resolve()
            if candidate.is_absolute()
            else (self.workspace_root / candidate).resolve()
        )


_workspace_env: ContextVar[dict[str, str] | None] = ContextVar("gtm_workspace_env", default=None)


def env_value(name: str, default: str = "") -> str:
    """Shell values take precedence; workspace values never leak into os.environ."""
    return os.environ.get(name, (_workspace_env.get() or {}).get(name, default)).strip()


def load_settings(path: Path | str = "gtm.yaml") -> Settings:
    config_path = Path(path).expanduser().resolve()
    if str(path) == "gtm.yaml" and not config_path.exists():
        config_path = next(
            (
                parent / "gtm.yaml"
                for parent in Path.cwd().parents
                if (parent / "gtm.yaml").exists()
            ),
            config_path,
        )
    root = config_path.parent
    _workspace_env.set(
        {key: value for key, value in dotenv_values(root / ".env").items() if value is not None}
    )
    if not config_path.exists():
        if str(path) != "gtm.yaml":
            raise FileNotFoundError(f"Configuration not found: {config_path}")
        return Settings(workspace_root=root)
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return Settings.model_validate({**data, "workspace_root": root})


def credential(name: str) -> str:
    value = env_value(name)
    if not value:
        raise RuntimeError(f"Missing {name}. Add it to .env; credentials are never CLI arguments.")
    return value


def has_supabase() -> bool:
    return bool(env_value("SUPABASE_URL") and env_value("SUPABASE_SERVICE_ROLE_KEY"))

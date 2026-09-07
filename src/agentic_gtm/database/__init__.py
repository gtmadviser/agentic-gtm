"""Operational stores. Supabase by default, CSV/JSON files as the no-database path."""

from __future__ import annotations

import sys

from ..config import Settings, has_supabase
from .base import TABLES, Store
from .files import FileStore
from .supabase import SupabaseStore


def open_store(settings: Settings | None = None, *, quiet: bool = False) -> Store:
    """Return the configured store.

    Resolution order: explicit `store.backend` in gtm.yaml, then `auto`, which
    prefers Supabase and falls back to files. The fallback is refused when the
    workspace policy `require_supabase_for_connected_workflows` is true.
    """
    settings = settings or Settings()
    backend = settings.store.backend
    if backend == "supabase" or (backend == "auto" and has_supabase()):
        if not has_supabase():
            raise RuntimeError(
                "store.backend is supabase but SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY "
                "are not set in .env"
            )
        return SupabaseStore()
    if settings.policies.require_supabase_for_connected_workflows:
        raise RuntimeError(
            "This workspace requires Supabase for connected workflows. Add SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY to .env, or set policies."
            "require_supabase_for_connected_workflows: false to use the files store."
        )
    store = FileStore(settings.resolve(settings.store.path))
    if backend == "auto" and not quiet:
        print(
            f"store: files ({store.root}); Supabase credentials not found, using CSV tables",
            file=sys.stderr,
        )
    return store


__all__ = ["TABLES", "FileStore", "Store", "SupabaseStore", "open_store"]

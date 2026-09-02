"""Provider adapter primitives."""

from __future__ import annotations

import time
from abc import ABC
from typing import Any

import httpx

from .. import __version__

USER_AGENT = f"agentic-gtm/{__version__} (+https://github.com/gtmadviser/agentic-gtm)"


class AdapterError(RuntimeError):
    """A provider operation failed without exposing credentials."""


class CapabilityError(AdapterError):
    """The provider does not implement the requested capability."""


class APIClient:
    def __init__(
        self,
        base_url: str,
        headers: dict[str, str],
        *,
        timeout: float = 45,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        # Several providers sit behind Cloudflare and reject requests with a
        # library-default user agent. Always send an explicit one.
        self.client = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={"User-Agent": USER_AGENT, **headers},
            timeout=timeout,
            transport=transport,
        )

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        last_error: Exception | None = None
        for attempt in range(4):
            try:
                response = self.client.request(method, path, **kwargs)
                if response.status_code == 429 or response.status_code >= 500:
                    if attempt == 3:
                        response.raise_for_status()
                    wait = min(float(response.headers.get("retry-after", 2**attempt)), 8)
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                return response.json() if response.content else {}
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = exc
                if attempt == 3:
                    break
                time.sleep(min(2**attempt, 4))
            except httpx.HTTPStatusError as exc:
                detail = exc.response.text[:300]
                raise AdapterError(
                    f"{method} {path} failed with HTTP {exc.response.status_code}: {detail}"
                ) from exc
        raise AdapterError(f"{method} {path} failed after retries: {last_error}")


class ProviderAdapter(ABC):
    name: str
    capabilities: frozenset[str] = frozenset()

    def require(self, capability: str) -> None:
        if capability not in self.capabilities:
            raise CapabilityError(f"{self.name} does not support {capability}")

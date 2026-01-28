#!/usr/bin/env python3
"""
Trails in the Database API client.

Small helper module to talk to the official TrailsDB REST API, as described
in `trailsdb-api.json`. For now we only implement the endpoint needed by the
scraper:

    GET /api/script/detail/{gameId}/{fname}
"""

from __future__ import annotations

from typing import Any, Dict, List

import requests


DEFAULT_BASE_URL = "https://trailsinthedatabase.com"


class TrailsDbApiError(Exception):
    """Raised when the TrailsDB API returns an error response."""


def _build_url(base_url: str, path: str) -> str:
    base = base_url.rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    return base + path


def get_script_detail(
    game_id: int,
    fname: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 10.0,
) -> List[Dict[str, Any]]:
    """
    Call the Script Detail API to get script entries for a given game/file.

    This wraps:
        GET /api/script/detail/{gameId}/{fname}

    Args:
        game_id: Game identifier (integer).
        fname: Script filename identifier (string).
        base_url: Base URL for the API host (default: https://trailsinthedatabase.com).
        timeout: Request timeout in seconds.

    Returns:
        List of Script objects (as dictionaries) as returned by the API.

    Raises:
        TrailsDbApiError: If the request fails or the response is not JSON.
    """
    url = _build_url(base_url, f"/api/script/detail/{game_id}/{fname}")

    try:
        response = requests.get(url, timeout=timeout)
    except requests.RequestException as exc:
        raise TrailsDbApiError(f"Failed to call TrailsDB API: {exc}") from exc

    if not response.ok:
        raise TrailsDbApiError(
            f"TrailsDB API returned HTTP {response.status_code} for {url}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise TrailsDbApiError("TrailsDB API returned non-JSON response") from exc

    if not isinstance(data, list):
        raise TrailsDbApiError(
            f"Unexpected response shape from TrailsDB API, expected list got {type(data)!r}"
        )

    return data


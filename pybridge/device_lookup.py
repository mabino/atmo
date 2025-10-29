"""Helpers for locating pyatv device configurations."""

from __future__ import annotations

from typing import List, Optional

from pyatv.interface import BaseConfig


def select_config(configs: List[BaseConfig], identifier: str) -> Optional[BaseConfig]:
    """Find a configuration matching identifier/name/address."""

    target = identifier.lower()
    for config in configs:
        if config.identifier and config.identifier.lower() == target:
            return config

        for candidate in config.all_identifiers:
            if candidate and candidate.lower() == target:
                return config

        name = getattr(config, "name", None)
        if name and name.lower() == target:
            return config

        try:
            if str(config.address) == identifier:
                return config
        except Exception:  # pragma: no cover - depends on config implementation
            continue

    return None

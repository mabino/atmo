"""Discovery helpers wrapping ``pyatv.scan``."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pyatv import scan
from pyatv.const import Protocol
from pyatv.interface import BaseConfig
from pyatv.interface import Storage

from .storage import load_storage

# Type alias for JSON-friendly payloads
DiscoveryPayload = Dict[str, Any]


@dataclass
class DiscoveryOptions:
    """User-specified options for discovery."""

    timeout: float = 5.0
    protocol: Optional[str] = None
    identifier: Optional[str] = None
    storage_path: Optional[str] = None
    use_storage: bool = True


async def discover_devices(options: DiscoveryOptions) -> List[DiscoveryPayload]:
    """Run ``pyatv.scan`` and return JSON serialisable device data."""

    loop = asyncio.get_running_loop()

    storage = None
    if options.use_storage:
        storage = await load_storage(loop, options.storage_path)

    configs = await scan_configs(options, storage=storage)

    return [_config_to_payload(config) for config in configs]


async def scan_configs(
    options: DiscoveryOptions, storage: Optional[Storage] = None
) -> List[BaseConfig]:
    """Run ``pyatv.scan`` and return raw configuration objects."""

    loop = asyncio.get_running_loop()

    storage_to_use = storage
    if storage_to_use is None and options.use_storage:
        storage_to_use = await load_storage(loop, options.storage_path)

    identifier = options.identifier

    protocol = None
    if options.protocol:
        try:
            protocol = Protocol[options.protocol]
        except KeyError as exc:
            raise ValueError(f"unknown protocol: {options.protocol}") from exc

    timeout = max(1, int(round(options.timeout)))

    return await scan(
        loop,
        timeout=timeout,
        identifier=identifier,
        protocol=protocol,
        storage=storage_to_use,
    )


def _config_to_payload(config: BaseConfig) -> DiscoveryPayload:
    """Convert a ``pyatv`` configuration to plain JSON data."""

    info = config.device_info

    payload: DiscoveryPayload = {
        "name": config.name,
        "address": str(config.address),
        "model": info.model_str,
        "deep_sleep": config.deep_sleep,
        "identifiers": config.all_identifiers,
        "main_identifier": config.identifier,
        "device_info": {
            "operating_system": info.operating_system.name,
            "version": info.version,
            "build_number": info.build_number,
            "model": info.model.name,
            "model_str": info.model_str,
            "raw_model": info.raw_model,
            "mac": info.mac,
        },
        "protocols": [
            {
                "protocol": service.protocol.name,
                "identifier": service.identifier,
                "port": service.port,
                "requires_password": service.requires_password,
                "pairing": service.pairing.name,
                "credentials_present": bool(service.credentials),
                "password_present": bool(service.password),
                "enabled": service.enabled,
            }
            for service in config.services
        ],
    }

    return payload


MOCK_DEVICES: List[DiscoveryPayload] = [
    {
        "name": "Living Room",
        "address": "10.0.0.10",
        "deep_sleep": False,
        "identifiers": ["00:11:22:33:44:55", "11223344-5566-7788-9900-112233445566"],
        "main_identifier": "11223344-5566-7788-9900-112233445566",
        "device_info": {
            "operating_system": "TvOS",
            "version": "17.5",
            "build_number": "21L570",
            "model": "AppleTV4KGen3",
            "model_str": "Apple TV 4K (3rd generation)",
            "raw_model": None,
            "mac": "aa:bb:cc:dd:ee:ff",
        },
        "protocols": [
            {
                "protocol": "Companion",
                "identifier": "11223344-5566-7788-9900-112233445566",
                "port": 49153,
                "requires_password": False,
                "pairing": "Mandatory",
                "credentials_present": True,
                "password_present": False,
                "enabled": True,
            },
            {
                "protocol": "AirPlay",
                "identifier": "00:11:22:33:44:55",
                "port": 7000,
                "requires_password": False,
                "pairing": "Mandatory",
                "credentials_present": True,
                "password_present": False,
                "enabled": True,
            },
        ],
    }
]


def mock_devices() -> List[DiscoveryPayload]:
    """Return deterministic mock discovery data."""

    # Return a deep copy to avoid accidental mutation across tests or runs
    return json.loads(json.dumps(MOCK_DEVICES))

"""Pairing helpers using pyatv."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Optional

from pyatv import exceptions as pyatv_exceptions
PYATV_ERROR = getattr(
    pyatv_exceptions,
    "PyatvError",
    getattr(pyatv_exceptions, "PyATVError", Exception),
)
from pyatv import pair as pyatv_pair
from pyatv.const import Protocol
from pyatv.interface import BaseConfig, Storage

from .discovery import DiscoveryOptions, scan_configs
from .device_lookup import select_config
from .storage import load_storage

DEFAULT_PIN = "1234"


class PairingError(Exception):
    """Raised when pairing cannot be completed."""


@dataclass
class PairingOptions:
    """Options provided by the CLI for pairing."""

    identifier: str
    protocol: str
    pin: Optional[str] = None
    display_name: str = "pyatv-bridge"
    storage_path: Optional[str] = None
    use_storage: bool = True
    mock: bool = False
    interactive: bool = False


@dataclass
class PairingResult:
    """Successful pairing result."""

    status: str
    identifier: Optional[str]
    protocol: str
    credentials_saved: bool
    credentials: Optional[str]


@dataclass
class PinRequiredResult:
    """Pairing result when a PIN must be provided by the user."""

    status: str
    identifier: Optional[str]
    protocol: str
    message: str


@dataclass
class UnpairOptions:
    """Options for removing stored credentials."""

    identifier: str
    protocol: str
    storage_path: Optional[str] = None
    use_storage: bool = True
    mock: bool = False


@dataclass
class UnpairResult:
    """Successful unpair result."""

    status: str
    identifier: Optional[str]
    protocol: str
    credentials_removed: bool


@dataclass
class PairingSession:
    """Active pairing session state for interactive flows."""

    pairing: Any
    config: BaseConfig
    protocol: Protocol
    storage: Optional[Storage]


async def pair_device(options: PairingOptions):
    """Pair a specific device and protocol."""

    if options.mock:
        if options.pin is None:
            return PinRequiredResult(
                status="pin_required",
                identifier=options.identifier,
                protocol=options.protocol,
                message="Provide the on-screen PIN and retry.",
            )

        return PairingResult(
            status="paired",
            identifier=options.identifier,
            protocol=options.protocol,
            credentials_saved=True,
            credentials="mock-credentials",
        )

    session = await create_pairing_session(options)
    pairing = session.pairing
    config = session.config
    protocol = session.protocol
    storage = session.storage

    try:
        await pairing.begin()

        if pairing.device_provides_pin:
            if options.pin is None:
                return PinRequiredResult(
                    status="pin_required",
                    identifier=config.identifier,
                    protocol=protocol.name,
                    message="Enter the PIN shown on the Apple TV screen.",
                )

            pairing.pin(options.pin)
        else:
            pairing.pin(options.pin or DEFAULT_PIN)

        await pairing.finish()

        if not pairing.has_paired:
            raise PairingError("pairing failed")

        if storage is not None:
            await storage.save()

        return PairingResult(
            status="paired",
            identifier=config.identifier,
            protocol=protocol.name,
            credentials_saved=True,
            credentials=pairing.service.credentials,
        )

    except pyatv_exceptions.PairingError as exc:
        raise PairingError(str(exc)) from exc
    finally:
        await pairing.close()


def _parse_protocol(value: str) -> Protocol:
    try:
        return Protocol[value]
    except KeyError as exc:
        raise PairingError(f"unknown protocol: {value}") from exc


async def unpair_device(options: UnpairOptions) -> UnpairResult:
    """Remove stored credentials for a device protocol."""

    if options.mock:
        return UnpairResult(
            status="unpaired",
            identifier=options.identifier,
            protocol=options.protocol,
            credentials_removed=True,
        )

    loop = asyncio.get_running_loop()

    if not options.use_storage:
        raise PairingError("storage is required to unpair")

    storage = await load_storage(loop, options.storage_path)
    protocol = _parse_protocol(options.protocol)

    configs = await scan_configs(
        DiscoveryOptions(
            timeout=5,
            protocol=None,
            identifier=None,
            storage_path=options.storage_path,
            use_storage=options.use_storage,
        ),
        storage=storage,
    )

    config = select_config(configs, options.identifier)
    if config is None:
        raise PairingError("device not found")

    settings = await storage.get_settings(config)
    removed = _clear_credentials(settings, protocol)

    if not removed:
        return UnpairResult(
            status="noop",
            identifier=config.identifier,
            protocol=protocol.name,
            credentials_removed=False,
        )

    await storage.save()

    return UnpairResult(
        status="unpaired",
        identifier=config.identifier,
        protocol=protocol.name,
        credentials_removed=True,
    )


def _clear_credentials(settings, protocol: Protocol) -> bool:
    cleared = False

    if protocol == Protocol.AirPlay:
        if settings.protocols.airplay.credentials or settings.protocols.airplay.password:
            settings.protocols.airplay.credentials = None
            settings.protocols.airplay.password = None
            cleared = True
    elif protocol == Protocol.Companion:
        if settings.protocols.companion.credentials:
            settings.protocols.companion.credentials = None
            cleared = True
    elif protocol == Protocol.RAOP:
        if settings.protocols.raop.credentials or settings.protocols.raop.password:
            settings.protocols.raop.credentials = None
            settings.protocols.raop.password = None
            cleared = True
    elif protocol == Protocol.MRP:
        if settings.protocols.mrp.credentials:
            settings.protocols.mrp.credentials = None
            cleared = True
    elif protocol == Protocol.DMAP:
        if settings.protocols.dmap.credentials:
            settings.protocols.dmap.credentials = None
            cleared = True

    return cleared


async def create_pairing_session(options: PairingOptions) -> PairingSession:
    """Create an active pairing session without completing it."""

    if options.mock:
        raise PairingError("mock pairing session not supported")

    loop = asyncio.get_running_loop()

    storage: Optional[Storage] = None
    if options.use_storage:
        storage = await load_storage(loop, options.storage_path)

    protocol = _parse_protocol(options.protocol)

    configs = await scan_configs(
        DiscoveryOptions(
            timeout=5,
            protocol=None,
            identifier=None,
            storage_path=options.storage_path,
            use_storage=options.use_storage,
        ),
        storage=storage,
    )

    config = select_config(configs, options.identifier)
    if config is None:
        raise PairingError("device not found")

    try:
        pairing = await pyatv_pair(
            config,
            protocol,
            loop,
            storage=storage,
            name=options.display_name,
        )
    except PYATV_ERROR as exc:  # pragma: no cover - defensive
        raise PairingError(str(exc)) from exc

    return PairingSession(pairing=pairing, config=config, protocol=protocol, storage=storage)

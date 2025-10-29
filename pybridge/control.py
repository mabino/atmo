"""Control and power command execution via pyatv."""

from __future__ import annotations

import asyncio
import inspect
import json
import sys
from dataclasses import dataclass
from typing import Any, Optional

from pyatv import connect
from pyatv import exceptions as pyatv_exceptions
from pyatv.const import DeviceState, InputAction, PowerState, Protocol
PYATV_ERROR = getattr(
    pyatv_exceptions,
    "PyatvError",
    getattr(pyatv_exceptions, "PyATVError", Exception),
)
from pyatv.interface import AppleTV, BaseConfig
from pyatv.interface import Storage

from .device_lookup import select_config
from .discovery import DiscoveryOptions, scan_configs
from .storage import load_storage


class ControlError(Exception):
    """Raised when sending a command fails."""


@dataclass
class CommandOptions:
    """Incoming CLI options for remote commands."""

    identifier: str
    command: str
    action: str = "SingleTap"
    protocol: Optional[str] = None
    storage_path: Optional[str] = None
    use_storage: bool = True
    mock: bool = False


@dataclass
class PowerOptions:
    """Incoming CLI options for power commands."""

    identifier: str
    action: str
    storage_path: Optional[str] = None
    use_storage: bool = True
    mock: bool = False


@dataclass
class SessionOptions:
    """Options for maintaining a persistent command session."""

    identifier: str
    storage_path: Optional[str] = None
    use_storage: bool = True
    mock: bool = False


async def execute_command(options: CommandOptions) -> dict:
    """Execute a remote control command."""

    if options.mock:
        return {
            "status": "ok",
            "identifier": options.identifier,
            "command": options.command,
            "action": options.action,
            "mock": True,
        }

    loop = asyncio.get_running_loop()

    storage: Optional[Storage] = None
    if options.use_storage:
        storage = await load_storage(loop, options.storage_path)

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
        raise ControlError("device not found")

    action = _parse_action(options.action)

    command = options.command.lower()

    atv = await _connect_device(config, loop, storage)

    try:
        await _invoke_remote(atv, command, action)
    finally:
        atv.close()

    return {
        "status": "ok",
        "identifier": config.identifier,
        "command": command,
        "action": action.name,
    }


async def execute_power(options: PowerOptions) -> dict:
    """Execute a power command."""

    if options.mock:
        return {
            "status": "ok",
            "identifier": options.identifier,
            "power": options.action,
            "mock": True,
        }

    loop = asyncio.get_running_loop()

    storage: Optional[Storage] = None
    if options.use_storage:
        storage = await load_storage(loop, options.storage_path)

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
        raise ControlError("device not found")

    atv = await _connect_device(config, loop, storage)

    try:
        power = atv.power
        action = options.action.lower()
        if action == "on":
            await power.turn_on()
        elif action == "off":
            await power.turn_off()
        elif action == "status":
            state = await _resolve_power_state(power)
            return {
                "status": "ok",
                "identifier": config.identifier,
                "power_state": state.name if isinstance(state, PowerState) else str(state),
            }
        else:
            raise ControlError(f"unknown power action: {options.action}")
    finally:
        atv.close()

    return {
        "status": "ok",
        "identifier": config.identifier,
        "power": options.action,
    }


async def _connect_device(
    config: BaseConfig,
    loop: asyncio.AbstractEventLoop,
    storage: Optional[Storage],
) -> AppleTV:
    try:
        return await connect(config, loop, storage=storage)
    except PYATV_ERROR as exc:
        raise ControlError(str(exc)) from exc


def _parse_action(name: str) -> InputAction:
    try:
        return InputAction[name]
    except KeyError as exc:
        raise ControlError(f"unknown input action: {name}") from exc


async def _invoke_remote(
    atv: AppleTV,
    command: str,
    action: InputAction,
) -> None:
    remote = atv.remote_control

    directional_commands = {
        "home": remote.home,
        "menu": remote.menu,
        "select": remote.select,
        "up": remote.up,
        "down": remote.down,
        "left": remote.left,
        "right": remote.right,
    }

    if command in directional_commands:
        await directional_commands[command](action=action)
        return

    if command in {"play_pause", "playpause"}:
        await _invoke_play_pause(atv)
        return

    raise ControlError(f"unsupported command: {command}")


async def _invoke_play_pause(atv: AppleTV) -> None:
    remote = atv.remote_control

    try:
        await remote.play_pause()
    except (pyatv_exceptions.CommandError, pyatv_exceptions.NotSupportedError) as exc:
        await _fallback_play_pause(atv, exc)
    except PYATV_ERROR as exc:
        raise ControlError(str(exc)) from exc


async def _fallback_play_pause(atv: AppleTV, original_exc: Exception) -> None:
    failure_message = str(original_exc) or "play/pause command failed"

    metadata = getattr(atv, "metadata", None)
    if metadata is None:
        raise ControlError(failure_message) from original_exc

    try:
        playing = await metadata.playing()
    except PYATV_ERROR as exc:  # pragma: no cover - defensive
        raise ControlError(failure_message) from exc

    state = getattr(playing, "device_state", None) or DeviceState.Idle
    remote = atv.remote_control

    try:
        if state == DeviceState.Playing:
            await remote.pause()
        else:
            await remote.play()
    except (pyatv_exceptions.CommandError, pyatv_exceptions.NotSupportedError) as exc:
        raise ControlError(str(exc)) from exc
    except PYATV_ERROR as exc:  # pragma: no cover - defensive
        raise ControlError(str(exc)) from exc


async def run_command_session(options: SessionOptions) -> int:
    """Maintain a persistent connection for command and power handling."""

    if options.mock:
        await _run_mock_session(options)
        return 0

    loop = asyncio.get_running_loop()

    storage: Optional[Storage] = None
    if options.use_storage:
        storage = await load_storage(loop, options.storage_path)

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
        _emit_session_payload({"status": "error", "error": "device not found", "fatal": True})
        return 2

    try:
        atv = await _connect_device(config, loop, storage)
    except ControlError as exc:
        _emit_session_payload({"status": "error", "error": str(exc), "fatal": True})
        return 2

    _emit_session_payload(
        {
            "status": "ready",
            "identifier": config.identifier,
            "name": getattr(config, "name", None),
        }
    )

    try:
        graceful = await _session_loop(atv)
    finally:
        atv.close()

    return 0 if graceful else 1


async def _session_loop(atv: AppleTV) -> bool:
    loop = asyncio.get_running_loop()
    fatal = False
    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            break

        message = line.strip()
        if not message:
            continue

        try:
            payload = json.loads(message)
        except json.JSONDecodeError:
            _emit_session_payload({"status": "error", "error": "invalid json"})
            continue

        msg_type = payload.get("type")
        should_continue = True
        if msg_type == "command":
            should_continue = await _session_handle_command(atv, payload)
        elif msg_type == "power":
            should_continue = await _session_handle_power(atv, payload)
        elif msg_type == "close":
            _emit_session_payload({"status": "closing"})
            break
        else:
            _emit_session_payload({"status": "error", "error": "unknown message type"})

        if not should_continue:
            fatal = True
            break

    return not fatal


async def _session_handle_command(atv: AppleTV, payload: dict) -> bool:
    command = payload.get("command")
    action_name = payload.get("action", "SingleTap")

    if not command:
        _emit_session_payload({"status": "error", "type": "command", "error": "missing command"})
        return True

    try:
        action = _parse_action(action_name)
        await _invoke_remote(atv, command.lower(), action)
    except ControlError as exc:
        _emit_session_payload(
            {
                "status": "error",
                "type": "command",
                "command": command,
                "error": str(exc),
            }
        )
        return True
    except PYATV_ERROR as exc:  # pragma: no cover - defensive
        _emit_session_payload(
            {
                "status": "error",
                "type": "command",
                "command": command,
                "error": str(exc),
                "fatal": True,
            }
        )
        return False

    _emit_session_payload(
        {
            "status": "ok",
            "type": "command",
            "command": command.lower(),
            "action": action.name,
        }
    )
    return True


async def _session_handle_power(atv: AppleTV, payload: dict) -> bool:
    action = payload.get("action")
    if not action:
        _emit_session_payload({"status": "error", "type": "power", "error": "missing action"})
        return True

    lower_action = str(action).lower()
    try:
        power = atv.power
        if lower_action == "on":
            await power.turn_on()
            result = {"power": "on"}
        elif lower_action == "off":
            await power.turn_off()
            result = {"power": "off"}
        elif lower_action == "status":
            state = await _resolve_power_state(power)
            value = state.name if isinstance(state, PowerState) else str(state)
            result = {"power_state": value}
        else:
            raise ControlError(f"unknown power action: {action}")
    except ControlError as exc:
        _emit_session_payload(
            {
                "status": "error",
                "type": "power",
                "action": action,
                "error": str(exc),
            }
        )
        return True
    except PYATV_ERROR as exc:  # pragma: no cover - defensive
        _emit_session_payload(
            {
                "status": "error",
                "type": "power",
                "action": action,
                "error": str(exc),
                "fatal": True,
            }
        )
        return False

    response = {"status": "ok", "type": "power"}
    response.update(result)
    _emit_session_payload(response)
    return True


async def _resolve_power_state(power: Any) -> Any:
    """Return the current power state supporting sync, async, and callable accessors."""

    try:
        attribute = power.power_state
    except AttributeError as exc:
        raise ControlError("power state not supported") from exc

    if callable(attribute):
        try:
            result = attribute()
        except TypeError:
            # Fall back to the raw attribute if the backend exposes a property-like callable.
            result = attribute
        else:
            if inspect.isawaitable(result):
                return await result
            return result

    if inspect.isawaitable(attribute):
        return await attribute

    return attribute


async def _run_mock_session(options: SessionOptions) -> None:
    loop = asyncio.get_running_loop()
    power_state = "off"

    _emit_session_payload(
        {
            "status": "ready",
            "identifier": options.identifier,
            "mock": True,
        }
    )

    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            break

        message = line.strip()
        if not message:
            continue

        try:
            payload = json.loads(message)
        except json.JSONDecodeError:
            _emit_session_payload({"status": "error", "error": "invalid json"})
            continue

        msg_type = payload.get("type")
        if msg_type == "command":
            command = payload.get("command", "")
            action = str(payload.get("action", "SingleTap"))
            _emit_session_payload(
                {
                    "status": "ok",
                    "type": "command",
                    "command": command.lower(),
                    "action": action,
                    "mock": True,
                }
            )
        elif msg_type == "power":
            action = str(payload.get("action", "status")).lower()
            if action == "on":
                power_state = "on"
                response = {"power": "on"}
            elif action == "off":
                power_state = "off"
                response = {"power": "off"}
            else:
                response = {"power_state": power_state}
            result = {"status": "ok", "type": "power"}
            result.update(response)
            _emit_session_payload(result)
        elif msg_type == "close":
            _emit_session_payload({"status": "closing", "mock": True})
            break
        else:
            _emit_session_payload({"status": "error", "error": "unknown message type"})


def _emit_session_payload(payload: dict) -> None:
    print(json.dumps(payload, separators=(",", ":")), flush=True)

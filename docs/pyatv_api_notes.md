# pyatv API Notes

Sources: `pyatv.dev` documentation (Development → Scan, Pair and Connect / Control / Power Management sections).

## Discovery & Scan
- `pyatv.scan(loop, timeout=5)` returns a list of `AppleTV` configuration entries.
- Each entry exposes identifiers accessible via `config.identifier`, `config.address`, etc.
- Discovery requires an asyncio loop.

## Pairing Workflow
- Pairing for each protocol is mandatory (Companion, AirPlay, RAOP) as noted in docs.
- CLI example `atvremote --id <id> --protocol airplay pair` prompts for PIN displayed on Apple TV.
- After pairing, credentials are stored automatically on disk using file-based storage (`pyatv.storage`), removing the need to re-supply credentials manually.
- Programmatic equivalent uses `pyatv.pair(config, protocol)` and asynchronous APIs to drive pairing and exchange PIN codes.

## Remote Control Interface
- Acquire via `atv = await pyatv.connect(config, loop)` then `remote = atv.remote_control`.
- Supported commands relevant to this app:
  - Navigation: `remote.up(action=InputAction.SingleTap)`, `.down`, `.left`, `.right`.
  - Selection: `remote.select()`, `remote.menu()`, `remote.home()`.
  - Playback: `remote.play_pause()` to toggle playback state.
- Input actions default to `InputAction.SingleTap`; hold/double tap options available if needed.

## Power Management Interface
- Access with `power = atv.power` after connecting.
- Provides `await power.turn_on()` and `await power.turn_off()` for tvOS devices.
- Current power state available via `await power.power_state()` (returns `PowerState` enum).

## Connection Lifecycle
- Always close the connection via `atv.close()` in a `finally` block.
- Use `asyncio.run` or event loop management to bridge from synchronous entry points.

## Credential Storage
- Default file storage used by bundled tools lives at `$HOME/.pyatv.conf`; use `FileStorage.default_storage(loop)` to share credentials with pyatv CLIs.
- Credentials and other settings are automatically persisted after successful pairing when storage is provided and `storage.save()` is called.
- `print_settings` command (and analogous APIs) expose saved credentials for debugging.

These notes inform the Python bridge CLI implementation and bridging contract with the Swift UI app.

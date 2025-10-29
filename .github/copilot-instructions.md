# Copilot Instructions

## Architecture
- macOS SwiftUI app (`AppleTVRemoteApp/Sources/...`) drives a Python CLI bridge (`pybridge/`) that wraps the `pyatv` library. Swift launches Python subprocesses via `BridgeService` and exchanges JSON.
- `BridgeViewModel` (MainActor) owns device discovery, selection, pairing state, and marshals requests to the `BridgeService` actor; UI layers should never talk to `BridgeService` directly.
- `BridgeService` spawns the embedded Python interpreter from `Resources/Python`, maintains long-lived interactive sessions per device for pairing, and normal commands use one-shot processes.
- Python side exposes subcommands in `pybridge/cli.py` that defer to helper modules (`discovery.py`, `control.py`, `pairing.py`, etc.) and return dataclass payloads serialised to JSON for Swift.

## SwiftUI Front End
- `ContentView` is the only window: sidebar lists devices and now hosts pairing/refresh controls; the detail pane shows remote and power panels styled via `HighlightedControlButtonStyle` and `statusBanner` for feedback.
- Selection highlighting is central to UX—device cards use accent tint with rounded borders; new controls should reuse that style for consistency.
- Keep async interaction in the view model: every button should call a `BridgeViewModel` method that wraps `Task {}` and updates `statusMessage` for UI feedback.
- Pairing is interactive: the initial call without a PIN triggers `pin_required`, which primes `BridgeService` to keep the Python session alive; when the user submits a PIN the view model calls `pairDevice` again and `BridgeService` streams the PIN into the existing session rather than launching a new process.
- `AtmoApp` owns window lifecycle: use the shared `openWindow()` helper for any new menu commands (current commands are `New Window` ⌘N and `New Pairing` ⌘⇧N) so restoration bookkeeping stays consistent.
- Window titles are hidden to prioritize consistent left-aligned system sidebar toggle behavior; do not reintroduce custom title setting or toolbar mutations.
- Use `DebugLog`/`OSLog` hooks already in `ContentView` when adding diagnostics so sidebar artifact tracking stays centralised.
- **Future Enhancement: Mini Atmo** - Compact floating remote UI mode (currently disabled). Requires proper window restoration with macOS controls; `updateWindowForMiniMode` function exists but unused. Toggle via menu command when implemented.
- **Shortcuts Integration**: Remote control buttons and power commands are exposed as App Intents in `RemoteControlIntents.swift`, allowing users to create Shortcuts that control Apple TV devices. The shared `BridgeViewModel` instance enables App Intents to work with the currently selected device. URL schemes (atmo://command) are also supported for Shortcuts automation.

## Python Bridge
- CLI entry (`pybridge/__main__.py` and `cli.py`) is the only surface the Swift process executes; when adding features expose them as subcommands with JSON output.
- `pairing.py` now exposes `create_pairing_session`; the `pair` CLI starts the session, emits a `pin_required` JSON message, and blocks waiting for a PIN on `stdin` so the same process can finish pairing once the Swift side writes the PIN.
- Device discovery lives in `discovery.py`, command/power helpers in `control.py`; keep network I/O async and return serialisable dataclasses.
- Python unit tests use `unittest` under `tests/` and mock `pyatv` interactions (`python -m pytest tests` is the expected runner even though tests inherit from `unittest`).

## Builds, Tests, Tooling
- Swift package builds via SPM: run `xcrun swift build` or `xcrun swift test` from `AppleTVRemoteApp/` (targets defined in `Package.swift`). Tests rely on small async delays (`Task.sleep`) to allow actor tasks to finish.
- Python environment is managed in `.venv`; install requirements with `python3 -m venv .venv && .venv/bin/pip install pyatv` before building or running tests.
- The release pipeline (`Scripts/release.sh`) rebuilds the Swift binary and copies the Python bundle prepared by `Scripts/package_python.sh`; keep new Python dependencies vendored through that script.

## Conventions & Gotchas
- `BridgeService` filters stderr warnings (e.g., LibreSSL) via `shouldIgnoreStderrMessage`; preserve/extend that list when stderr noise appears, otherwise pairing sessions end prematurely.
- All Swift async calls must remain on the main actor when mutating published state—create helper methods in `BridgeViewModel` instead of capturing `@State` directly inside views.
- Refreshing devices uses `refreshDevices(mock:)`; always pass the current mock flag from UI controls to keep simulator mode coherent.
- Changes to command sets require updates in both Swift (`BridgeViewModel.sendCommand`) and Python (`pybridge/control.py` plus CLI parsing) so JSON payloads stay aligned.
- When adding menu actions, extend the `.commands` builder in `AtmoApp.swift`; we intentionally replace most default File actions and provide our own Close item.
- Release artifacts expect resources under `AppleTVRemoteApp/Sources/Atmo/Resources/Python`; keep relative paths consistent with `BridgeService.resolvePythonExecutable`.

Please let me know if any section is unclear or if more detail is needed for your workflows.

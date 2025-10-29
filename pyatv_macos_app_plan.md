# PyATV macOS Remote App — Project Plan

## Objectives
- Build a SwiftUI-based macOS GUI that discovers, pairs with, and controls Apple TV devices via the `pyatv` Python library.
- Provide pairing, power management (on/off), and remote control actions (home, menu, play/pause, directional taps).
- Supply automated tests that prove the app compiles, launches, and issues Python bridge calls to `pyatv` APIs.

## Scope & Constraints
- Platform: macOS 13+ with SwiftUI and Swift Concurrency.
- Python: CPython 3.11+ with the `pyatv` package available via virtual environment.
- Communication: Swift app shells out to a Python bridge executable (using `Process`) that wraps `pyatv` APIs.
- Credentials: rely on `pyatv` built-in storage for paired credentials; store bridge configuration under the user's Application Support directory.
- Testing: use `xcodebuild` (or `swift build`) plus XCTest UI/unit suites; provide a mock mode for the Python bridge so tests avoid device dependencies.

## High-Level Architecture
1. **Python Bridge Package** (`pybridge/`)
   - CLI entry point using `argparse` with subcommands: `scan`, `pair`, `command` (power, remote buttons).
   - Core module wraps `pyatv` async APIs (`scan`, `pair`, `connect`, `remote_control`, `power`).
   - Optional `--mock` flag for deterministic responses in automated tests.

2. **Swift macOS App** (`AppleTVRemoteApp/Sources/Atmo`)
   - SwiftUI app target with MVVM structure.
   - `PyATVBridgeService` invokes Python bridge via `Process` and decodes JSON responses.
   - UI: device list, pairing workflow, remote control buttons, and connection status.
   - App configuration stored via `AppStorage` / `UserDefaults` for selected device.

3. **Automated Tests**
   - Swift unit tests mocking `Process` output to validate JSON decoding and command routing.
   - UI tests launching the app, navigating basic flow using stub/mock mode.
   - Python unit tests using `pytest` (or `unittest`) to confirm bridge command parsing and `pyatv` API calls (mocked).
   - End-to-end script to run: create virtualenv, install deps, run Python tests, build macOS app, execute Swift tests with bridge in mock mode.

## Work Breakdown Structure
1. **Environment & Tooling**
   - [x] Verify Python environment and install `pyatv`.
   - [x] Document prerequisites (Python version, virtualenv, Xcode command-line tools).

2. **Documentation Review & Requirements Detailing**
   - [x] Extract pairing, power, remote API specifics from `pyatv.dev` docs.
   - [x] Identify required credentials storage paths.

3. **Python Bridge Implementation**
   - [x] Scaffold Python package with CLI entry point.
   - [x] Implement device scan and JSON output.
   - [x] Implement pairing flow (prompt for PIN via CLI/stdin JSON protocol) with persistent credentials.
   - [x] Implement remote commands (home/menu/play/pause/up/down/left/right/select) via `interface.RemoteControl`.
   - [x] Implement power commands via `interface.Power`.
   - [x] Add mock mode and unit tests.

4. **Swift macOS App Implementation**
   - [x] Initialize SwiftUI macOS app project structure (SPM-based target under `AppleTVRemoteApp/`).
   - [x] Build models (`BridgeDevice`, bridge service) and glue to the Python CLI.
   - [x] Implement pairing UI workflow (device picker, PIN entry modal, pairing state management).
   - [x] Create remote control UI (buttons, power panel, menu commands) wired to bridge service.
   - [x] Handle power controls, periodic status polling, and command feedback.
   - [x] Expose remote buttons and power controls to macOS Shortcuts via App Intents.
   - [x] Provide error handling, status banners, logging, and loading indicators.

5. **Testing & Automation**
   - [x] Author Swift unit tests around BridgeViewModel and storage using mocked services.
   - [ ] Add Swift UI tests launching the app with mocked bridge.
   - [x] Add Python unit tests for CLI argument parsing and pyatv call hooks.
   - [ ] Write integration script (`Scripts/run_all_tests.sh`) orchestrating lint/build/test steps, executing Swift tests with mock bridge, verifying app build.

6. **Documentation & Packaging**
   - [x] Document setup instructions (README covers environment setup, mock mode, and build steps).
   - [x] Describe test execution steps and mock mode usage within README/docs.
   - [ ] Outline future enhancements (AirPlay metadata, volume control, Mini Atmo compact floating remote UI, etc.).

## Risk & Mitigation Log
- **pyatv Not Installed**: Provide bootstrap script to set up venv and pip install `pyatv`.
- **Pairing Requires Physical AppleTV**: Offer mock responses and clearly document need for real device to complete pairing.
- **Process Communication Latency**: Use async/await with `Task` to avoid blocking UI; display progress indicators.
- **macOS Sandbox Permissions**: Ensure Python bridge path is accessible; consider bundling script within app resources and validating execution permissions.

## Known Issues / Bug Backlog
- **Toolbar double-arrow artifact**: Toggling the sidebar briefly reveals the system `toggleSidebar` button and can interfere with the Mock toolbar control. Logging is in place to trace window title updates, but the artifact still occurs and needs a future fix.

## Acceptance Criteria Checklist
 - [x] Project compiles via `xcodebuild`/`swift build` on macOS.
 - [x] App lists devices (mock or real) and initiates pairing through bridge.
 - [x] Remote buttons trigger corresponding Python bridge commands.
 - [x] Power commands reach Python bridge and return status.
 - [x] Automated tests cover Python CLI (mocked pyatv interactions).
 - [x] Swift unit tests validate bridge integration and UI wiring. (UI tests still pending.)
 - [ ] `Scripts/run_all_tests.sh` completes without failures, demonstrating build + tests.

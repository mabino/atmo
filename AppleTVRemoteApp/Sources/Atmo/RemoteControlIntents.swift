import AppIntents
import Foundation

// MARK: - Remote Control Commands

struct SendUpCommandIntent: AppIntent {
    static let title: LocalizedStringResource = "Apple TV Remote: Up"
    static let description: LocalizedStringResource = "Send up arrow command to Apple TV"

    @MainActor
    func perform() async throws -> some IntentResult {
        let viewModel = await getBridgeViewModel()
        viewModel.sendCommand("up")
        return .result()
    }
}

struct SendDownCommandIntent: AppIntent {
    static let title: LocalizedStringResource = "Apple TV Remote: Down"
    static let description: LocalizedStringResource = "Send down arrow command to Apple TV"

    @MainActor
    func perform() async throws -> some IntentResult {
        let viewModel = await getBridgeViewModel()
        viewModel.sendCommand("down")
        return .result()
    }
}

struct SendLeftCommandIntent: AppIntent {
    static let title: LocalizedStringResource = "Apple TV Remote: Left"
    static let description: LocalizedStringResource = "Send left arrow command to Apple TV"

    @MainActor
    func perform() async throws -> some IntentResult {
        let viewModel = await getBridgeViewModel()
        viewModel.sendCommand("left")
        return .result()
    }
}

struct SendRightCommandIntent: AppIntent {
    static let title: LocalizedStringResource = "Apple TV Remote: Right"
    static let description: LocalizedStringResource = "Send right arrow command to Apple TV"

    @MainActor
    func perform() async throws -> some IntentResult {
        let viewModel = await getBridgeViewModel()
        viewModel.sendCommand("right")
        return .result()
    }
}

struct SendSelectCommandIntent: AppIntent {
    static let title: LocalizedStringResource = "Apple TV Remote: Select"
    static let description: LocalizedStringResource = "Send select command to Apple TV"

    @MainActor
    func perform() async throws -> some IntentResult {
        let viewModel = await getBridgeViewModel()
        viewModel.sendCommand("select")
        return .result()
    }
}

struct SendMenuCommandIntent: AppIntent {
    static let title: LocalizedStringResource = "Apple TV Remote: Menu"
    static let description: LocalizedStringResource = "Send menu command to Apple TV"

    @MainActor
    func perform() async throws -> some IntentResult {
        let viewModel = await getBridgeViewModel()
        viewModel.sendCommand("menu")
        return .result()
    }
}

struct SendHomeCommandIntent: AppIntent {
    static let title: LocalizedStringResource = "Apple TV Remote: Home"
    static let description: LocalizedStringResource = "Send home command to Apple TV"

    @MainActor
    func perform() async throws -> some IntentResult {
        let viewModel = await getBridgeViewModel()
        viewModel.sendCommand("home")
        return .result()
    }
}

struct SendHomeHoldCommandIntent: AppIntent {
    static let title: LocalizedStringResource = "Apple TV Remote: Home (Hold)"
    static let description: LocalizedStringResource = "Send home hold command to Apple TV"

    @MainActor
    func perform() async throws -> some IntentResult {
        let viewModel = await getBridgeViewModel()
        viewModel.sendCommand("home", action: "Hold")
        return .result()
    }
}

struct SendPlayPauseCommandIntent: AppIntent {
    static let title: LocalizedStringResource = "Apple TV Remote: Play/Pause"
    static let description: LocalizedStringResource = "Send play/pause command to Apple TV"

    @MainActor
    func perform() async throws -> some IntentResult {
        let viewModel = await getBridgeViewModel()
        viewModel.sendCommand("play_pause")
        return .result()
    }
}

// MARK: - Power Commands

struct TurnOnAppleTVIntent: AppIntent {
    static let title: LocalizedStringResource = "Apple TV: Turn On"
    static let description: LocalizedStringResource = "Turn on the Apple TV"

    @MainActor
    func perform() async throws -> some IntentResult {
        let viewModel = await getBridgeViewModel()
        viewModel.togglePowerState() // This will turn on if currently off
        return .result()
    }
}

struct TurnOffAppleTVIntent: AppIntent {
    static let title: LocalizedStringResource = "Apple TV: Turn Off"
    static let description: LocalizedStringResource = "Turn off the Apple TV"

    @MainActor
    func perform() async throws -> some IntentResult {
        let viewModel = await getBridgeViewModel()
        viewModel.togglePowerState() // This will turn off if currently on
        return .result()
    }
}

struct CheckAppleTVPowerStatusIntent: AppIntent {
    static let title: LocalizedStringResource = "Apple TV: Check Power Status"
    static let description: LocalizedStringResource = "Check the current power status of the Apple TV"

    @MainActor
    func perform() async throws -> some IntentResult {
        let viewModel = await getBridgeViewModel()
        viewModel.requestPowerState()
        return .result()
    }
}

// MARK: - Helper Functions

/// Get the shared BridgeViewModel instance
@MainActor
private func getBridgeViewModel() async -> BridgeViewModel {
    return BridgeViewModel.shared
}
import Foundation

protocol BridgeDeviceCaching: Actor {
    func rememberDevicesValue() async -> Bool
    func setRememberDevices(enabled: Bool) async
    func loadSavedDevices() async -> [BridgeDevice]?
    func save(devices: [BridgeDevice]) async
    func clearSavedDevices() async
    func loadLastSelectedDeviceIdentifier() async -> String?
    func saveLastSelectedDeviceIdentifier(_ identifier: String?) async
    func showDeviceIPsValue() async -> Bool
    func setShowDeviceIPs(enabled: Bool) async
    func showOnlyAppleTVsValue() async -> Bool
    func setShowOnlyAppleTVs(enabled: Bool) async
    func showDevicePowerStateValue() async -> Bool
    func setShowDevicePowerState(enabled: Bool) async
}

actor BridgeDeviceCache: BridgeDeviceCaching {
    private let defaults: UserDefaults
    private let rememberKey = "BridgeDeviceCache.rememberDevices"
    private let devicesKey = "BridgeDeviceCache.devices"
    private let lastSelectedKey = "BridgeDeviceCache.lastSelectedDevice"
    private let showIPKey = "BridgeDeviceCache.showDeviceIPs"
    private let showAppleTVKey = "BridgeDeviceCache.showOnlyAppleTVs"
    private let showPowerStateKey = "BridgeDeviceCache.showDevicePowerState"

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    func rememberDevicesValue() async -> Bool {
        guard defaults.object(forKey: rememberKey) != nil else {
            return true
        }
        return defaults.bool(forKey: rememberKey)
    }

    func setRememberDevices(enabled: Bool) async {
        defaults.set(enabled, forKey: rememberKey)
    }

    func loadSavedDevices() async -> [BridgeDevice]? {
        guard let data = defaults.data(forKey: devicesKey) else {
            return nil
        }
        do {
            return try JSONDecoder().decode([BridgeDevice].self, from: data)
        } catch {
            defaults.removeObject(forKey: devicesKey)
            return nil
        }
    }

    func save(devices: [BridgeDevice]) async {
        guard !devices.isEmpty else {
            defaults.removeObject(forKey: devicesKey)
            return
        }
        do {
            let data = try JSONEncoder().encode(devices)
            defaults.set(data, forKey: devicesKey)
        } catch {
            defaults.removeObject(forKey: devicesKey)
        }
    }

    func clearSavedDevices() async {
        defaults.removeObject(forKey: devicesKey)
        defaults.removeObject(forKey: lastSelectedKey)
    }

    func loadLastSelectedDeviceIdentifier() async -> String? {
        defaults.string(forKey: lastSelectedKey)
    }

    func saveLastSelectedDeviceIdentifier(_ identifier: String?) async {
        if let identifier {
            defaults.set(identifier, forKey: lastSelectedKey)
        } else {
            defaults.removeObject(forKey: lastSelectedKey)
        }
    }

    func showDeviceIPsValue() async -> Bool {
        defaults.bool(forKey: showIPKey)
    }

    func setShowDeviceIPs(enabled: Bool) async {
        defaults.set(enabled, forKey: showIPKey)
    }

    func showOnlyAppleTVsValue() async -> Bool {
        guard defaults.object(forKey: showAppleTVKey) != nil else {
            return true
        }
        return defaults.bool(forKey: showAppleTVKey)
    }

    func setShowOnlyAppleTVs(enabled: Bool) async {
        defaults.set(enabled, forKey: showAppleTVKey)
    }

    func showDevicePowerStateValue() async -> Bool {
        defaults.bool(forKey: showPowerStateKey)
    }

    func setShowDevicePowerState(enabled: Bool) async {
        defaults.set(enabled, forKey: showPowerStateKey)
    }
}

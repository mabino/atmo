import AppKit
import SwiftUI
import Combine

struct DeviceInfoRow: Equatable {
    let label: String
    let value: String
}

enum DeviceInfoFormatter {
    static func windowTitle(for device: BridgeDevice?) -> String {
        guard let device else { return "Device Info" }
        return "\(device.name) Info"
    }

    static func rows(
        for device: BridgeDevice,
        isPaired: Bool,
        lastKnownPowerState: PowerStateStatus?
    ) -> [DeviceInfoRow] {
        var rows: [DeviceInfoRow] = []
        rows.append(DeviceInfoRow(label: "Name", value: device.name))
        rows.append(DeviceInfoRow(label: "Model", value: device.model ?? "Unknown"))
        rows.append(DeviceInfoRow(label: "IP Address", value: device.address))
        rows.append(DeviceInfoRow(label: "Identifier", value: device.id))

        let otherIdentifiers = device.identifiers.filter { $0 != device.id }
        if !otherIdentifiers.isEmpty {
            rows.append(DeviceInfoRow(
                label: otherIdentifiers.count == 1 ? "Other Identifier" : "Other Identifiers",
                value: otherIdentifiers.joined(separator: "\n")
            ))
        }

        rows.append(DeviceInfoRow(label: "Paired", value: isPaired ? "Yes" : "No"))

        let powerState = lastKnownPowerState ?? device.powerState
        let powerValue: String
        switch powerState {
        case .on: powerValue = "On"
        case .off: powerValue = "Off"
        case nil: powerValue = "Unknown"
        }
        rows.append(DeviceInfoRow(label: "Power State", value: powerValue))
        rows.append(DeviceInfoRow(label: "Deep Sleep", value: device.deepSleep ? "Yes" : "No"))
        return rows
    }

    static func protocolRows(for bridgeProtocol: BridgeProtocol) -> [DeviceInfoRow] {
        var rows: [DeviceInfoRow] = []
        rows.append(DeviceInfoRow(label: "Port", value: String(bridgeProtocol.port)))
        rows.append(DeviceInfoRow(label: "Pairing", value: bridgeProtocol.pairing.capitalized))
        rows.append(DeviceInfoRow(
            label: "Credentials",
            value: bridgeProtocol.credentialsPresent ? "Stored" : "Not stored"
        ))
        if bridgeProtocol.requiresPassword {
            rows.append(DeviceInfoRow(
                label: "Password",
                value: bridgeProtocol.passwordPresent ? "Stored" : "Required, not stored"
            ))
        }
        rows.append(DeviceInfoRow(label: "Enabled", value: bridgeProtocol.enabled ? "Yes" : "No"))
        return rows
    }
}

@MainActor
final class DeviceInfoWindowController: NSWindowController {
    static let shared = DeviceInfoWindowController()

    private var configuredViewModel: BridgeViewModel?
    private var titleCancellable: AnyCancellable?

    private init() {
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 420, height: 480),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.title = DeviceInfoFormatter.windowTitle(for: nil)
        window.isReleasedWhenClosed = false
        super.init(window: window)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    func showInfo(using viewModel: BridgeViewModel) {
        guard let window else { return }

        if configuredViewModel !== viewModel {
            configuredViewModel = viewModel
            let hostingView = NSHostingView(
                rootView: DeviceInfoView().environmentObject(viewModel)
            )
            window.contentView = hostingView
            titleCancellable = viewModel.$selectedDevice
                .receive(on: DispatchQueue.main)
                .sink { [weak window] device in
                    window?.title = DeviceInfoFormatter.windowTitle(for: device)
                }
        }

        window.title = DeviceInfoFormatter.windowTitle(for: viewModel.selectedDevice)
        if !window.isVisible {
            window.center()
        }
        window.makeKeyAndOrderFront(nil)
        NSApplication.shared.activate(ignoringOtherApps: true)
    }
}

private struct DeviceInfoView: View {
    @EnvironmentObject private var viewModel: BridgeViewModel

    var body: some View {
        Group {
            if let device = viewModel.selectedDevice {
                deviceDetails(for: device)
            } else {
                noSelection
            }
        }
        .frame(minWidth: 380, minHeight: 320)
    }

    private var noSelection: some View {
        VStack(spacing: 8) {
            Image(systemName: "info.circle")
                .font(.system(size: 36))
                .foregroundStyle(.secondary)
            Text("No Device Selected")
                .font(.headline)
            Text("Select a device in the sidebar to see its details.")
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding(24)
    }

    private func deviceDetails(for device: BridgeDevice) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                header(for: device)
                Divider()
                rowGrid(DeviceInfoFormatter.rows(
                    for: device,
                    isPaired: viewModel.pairedDeviceIDs.contains(device.id),
                    lastKnownPowerState: viewModel.lastKnownPowerState
                ))

                if !device.protocols.isEmpty {
                    Divider()
                    Text("Protocols")
                        .font(.headline)
                    ForEach(device.protocols) { bridgeProtocol in
                        VStack(alignment: .leading, spacing: 6) {
                            Text(bridgeProtocol.protocolName.capitalized)
                                .font(.subheadline)
                                .bold()
                            rowGrid(DeviceInfoFormatter.protocolRows(for: bridgeProtocol))
                        }
                        .padding(10)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .fill(.quaternary)
                        )
                    }
                }
            }
            .padding(24)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private func header(for device: BridgeDevice) -> some View {
        HStack(spacing: 12) {
            Image(systemName: device.isAppleTV ? "appletv.fill" : "network")
                .font(.system(size: 32))
                .foregroundStyle(.secondary)
            VStack(alignment: .leading, spacing: 2) {
                Text(device.name)
                    .font(.title2)
                    .bold()
                Text(device.model ?? device.address)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
        }
    }

    private func rowGrid(_ rows: [DeviceInfoRow]) -> some View {
        Grid(alignment: .leadingFirstTextBaseline, horizontalSpacing: 12, verticalSpacing: 6) {
            ForEach(rows, id: \.label) { row in
                GridRow {
                    Text(row.label)
                        .foregroundStyle(.secondary)
                        .gridColumnAlignment(.trailing)
                    Text(row.value)
                        .textSelection(.enabled)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
            }
        }
    }
}

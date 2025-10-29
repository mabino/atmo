import AppKit
import SwiftUI

@MainActor
final class HelpWindowController: NSWindowController {
    static let shared = HelpWindowController()

    private init() {
        let contentView = HelpContentView()
        let hostingView = NSHostingView(rootView: contentView)
        hostingView.translatesAutoresizingMaskIntoConstraints = false

        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 480, height: 360),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
    window.title = "Atmo Help"
        window.isReleasedWhenClosed = false
        window.contentView = NSView()
        window.contentView?.addSubview(hostingView)

        NSLayoutConstraint.activate([
            hostingView.leadingAnchor.constraint(equalTo: window.contentView!.leadingAnchor),
            hostingView.trailingAnchor.constraint(equalTo: window.contentView!.trailingAnchor),
            hostingView.topAnchor.constraint(equalTo: window.contentView!.topAnchor),
            hostingView.bottomAnchor.constraint(equalTo: window.contentView!.bottomAnchor)
        ])

        super.init(window: window)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    func showHelp() {
        if let window, !window.isVisible {
            window.center()
        }
        window?.makeKeyAndOrderFront(nil)
        NSApplication.shared.activate(ignoringOtherApps: true)
    }
}

private struct HelpContentView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Atmo Help")
                    .font(.title)
                    .bold()

                Text("Get started controlling your Apple TV in just a few steps.")

                Divider()

                VStack(alignment: .leading, spacing: 8) {
                    Text("Discover Devices")
                        .font(.headline)
                    Text("Use the sidebar to scan for nearby Apple TV devices. Paired devices appear at the top for quick access.")
                }

                VStack(alignment: .leading, spacing: 8) {
                    Text("Pair and Control")
                        .font(.headline)
                    Text("Select a device and choose a protocol to pair. Once paired, the remote controls and power commands become available in the detail view.")
                }

                VStack(alignment: .leading, spacing: 8) {
                    Text("Need More Help?")
                        .font(.headline)
                    Text("Visit the project README for setup instructions, or file an issue on GitHub if you run into trouble.")
                }
            }
            .padding(24)
        }
        .frame(minWidth: 420, minHeight: 300)
    }
}

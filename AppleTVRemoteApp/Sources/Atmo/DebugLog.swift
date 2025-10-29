#if DEBUG
import Foundation

struct DebugLogEntry: Identifiable, Hashable {
    let id = UUID()
    let timestamp: Date
    let message: String
}

actor DebugLog {
    static let shared = DebugLog()
    private let capacity = 200
    private var entries: [DebugLogEntry] = []

    func append(_ message: String) {
        let entry = DebugLogEntry(timestamp: Date(), message: message)
        entries.append(entry)
        if entries.count > capacity {
            entries.removeFirst(entries.count - capacity)
        }
        Task { @MainActor in
            NotificationCenter.default.post(name: .debugLogUpdated, object: nil)
        }
    }

    func entriesSnapshot() -> [DebugLogEntry] {
        entries
    }

    func clear() {
        entries.removeAll()
        Task { @MainActor in
            NotificationCenter.default.post(name: .debugLogUpdated, object: nil)
        }
    }
}

extension Notification.Name {
    static let debugLogUpdated = Notification.Name("DebugLogUpdated")
}
#endif

import Foundation
import Darwin

/// Decides whether the app is running from an approved install location
/// (/Applications or the real ~/Applications), so the "move to Applications"
/// prompt is only shown when it genuinely is somewhere else.
enum AppLocationCheck {
    static func approvedInstallDirectories(realHome: String = realUserHome()) -> [URL] {
        let systemApplications = URL(fileURLWithPath: "/Applications", isDirectory: true)
        let userApplications = URL(fileURLWithPath: realHome, isDirectory: true)
            .appendingPathComponent("Applications", isDirectory: true)
        return [systemApplications, userApplications]
    }

    /// Under App Sandbox, homeDirectoryForCurrentUser is the container home
    /// (~/Library/Containers/…), which would make ~/Applications never match.
    /// Resolve the real home via the passwd database instead.
    static func realUserHome() -> String {
        String(cString: getpwuid(getuid()).pointee.pw_dir)
    }

    static func isInApprovedLocation(bundleURL: URL, approvedDirectories: [URL]) -> Bool {
        let parentPath = bundleURL.resolvingSymlinksInPath()
            .deletingLastPathComponent()
            .standardizedFileURL.path
        return approvedDirectories.contains { allowed in
            let allowedPath = allowed.standardizedFileURL.path
            return parentPath == allowedPath || parentPath.hasPrefix(allowedPath + "/")
        }
    }

    /// Gatekeeper app translocation runs a quarantined app from a randomized
    /// read-only mount (/private/var/…/AppTranslocation/…), so the bundle URL
    /// no longer reflects where the user actually put the app. Map the running
    /// URL back to the on-disk original when translocated.
    static func untranslocatedBundleURL(for bundleURL: URL) -> URL? {
        guard let security = dlopen("/System/Library/Frameworks/Security.framework/Security", RTLD_LAZY) else {
            return nil
        }
        defer { dlclose(security) }

        typealias IsTranslocatedFn = @convention(c) (
            CFURL, UnsafeMutablePointer<Bool>, UnsafeMutablePointer<Unmanaged<CFError>?>?
        ) -> Bool
        typealias OriginalPathFn = @convention(c) (
            CFURL, UnsafeMutablePointer<Unmanaged<CFError>?>?
        ) -> Unmanaged<CFURL>?

        guard let isTranslocatedSym = dlsym(security, "SecTranslocateIsTranslocatedURL"),
              let originalPathSym = dlsym(security, "SecTranslocateCreateOriginalPathForURL") else {
            return nil
        }

        let isTranslocated = unsafeBitCast(isTranslocatedSym, to: IsTranslocatedFn.self)
        let originalPath = unsafeBitCast(originalPathSym, to: OriginalPathFn.self)

        var translocated = false
        guard isTranslocated(bundleURL as CFURL, &translocated, nil), translocated else {
            return nil
        }
        return originalPath(bundleURL as CFURL, nil)?.takeRetainedValue() as URL?
    }

    /// The URL to judge the install location by: the translocation original
    /// when running translocated, otherwise the bundle URL itself.
    static func effectiveBundleURL(for bundleURL: URL = Bundle.main.bundleURL) -> URL {
        untranslocatedBundleURL(for: bundleURL) ?? bundleURL
    }
}

#!/usr/bin/env swift
//
// generate_icon.swift: Programmatically render Atmo's app icon — a Siri-style
// remote with a touchpad ring, buttons, and a volume pill on a dark squircle —
// and keep the web assets (SVG favicon/logo) in lockstep with the same geometry.
//
// Usage: xcrun swift AppleTVRemoteApp/Scripts/generate_icon.swift [preview.png]
//   With an argument, renders only a 1024px preview PNG to that path.
//   Without, writes RemoteHelp.iconset + RemoteHelp.icns into the app
//   resources and the matching SVGs into Resources/ and docs/assets/images/.

import AppKit

let canvas: CGFloat = 1024

func color(_ hex: UInt32, _ alpha: CGFloat = 1.0) -> NSColor {
    NSColor(srgbRed: CGFloat((hex >> 16) & 0xFF) / 255,
            green: CGFloat((hex >> 8) & 0xFF) / 255,
            blue: CGFloat(hex & 0xFF) / 255,
            alpha: alpha)
}

// Palette: keep the existing identity (dark navy squircle, off-white remote)
let bgTop     = color(0x1F2937)
let bgBottom  = color(0x111827)
let bodyWhite = color(0xF9FAFB)
let buttonInk = color(0x1F2937, 0.92)

// Geometry shared by the PNG renderer and the SVG writer (y-down, SVG-style;
// the AppKit renderer flips). All values are on the 1024 canvas.
let squircleRadius = canvas * 0.2237
struct G {
    static let body       = (x: 392.0, y: 192.0, w: 240.0, h: 640.0, r: 120.0)
    static let ring       = (cx: 512.0, cy: 330.0, r: 78.0, stroke: 20.0)
    static let dotLeft    = (cx: 462.0, cy: 470.0, r: 22.0)
    static let dotRight   = (cx: 562.0, cy: 470.0, r: 22.0)
    static let volumePill = (x: 490.0, y: 584.0, w: 44.0, h: 140.0, r: 22.0)
}

func flip(_ y: Double, _ h: Double = 0) -> CGFloat { CGFloat(canvas) - CGFloat(y) - CGFloat(h) }

func drawIcon() {
    // Dark squircle, filling the canvas edge to edge (Tahoe style)
    let squircle = NSBezierPath(
        roundedRect: NSRect(x: 0, y: 0, width: canvas, height: canvas),
        xRadius: squircleRadius, yRadius: squircleRadius)
    squircle.addClip()
    NSGradient(colors: [bgTop, bgBottom])!
        .draw(in: NSRect(x: 0, y: 0, width: canvas, height: canvas), angle: -90)

    // Remote body
    bodyWhite.setFill()
    NSBezierPath(
        roundedRect: NSRect(x: G.body.x, y: flip(G.body.y, G.body.h),
                            width: G.body.w, height: G.body.h),
        xRadius: G.body.r, yRadius: G.body.r).fill()

    // Touchpad ring
    let ringRect = NSRect(x: G.ring.cx - G.ring.r, y: flip(G.ring.cy) - G.ring.r,
                          width: G.ring.r * 2, height: G.ring.r * 2)
    let ring = NSBezierPath(ovalIn: ringRect)
    ring.lineWidth = G.ring.stroke
    buttonInk.setStroke()
    ring.stroke()

    // Button dots
    buttonInk.setFill()
    for dot in [G.dotLeft, G.dotRight] {
        NSBezierPath(ovalIn: NSRect(x: dot.cx - dot.r, y: flip(dot.cy) - dot.r,
                                    width: dot.r * 2, height: dot.r * 2)).fill()
    }

    // Volume pill
    NSBezierPath(
        roundedRect: NSRect(x: G.volumePill.x, y: flip(G.volumePill.y, G.volumePill.h),
                            width: G.volumePill.w, height: G.volumePill.h),
        xRadius: G.volumePill.r, yRadius: G.volumePill.r).fill()
}

func svg(size: Int) -> String {
    """
    <?xml version="1.0" encoding="UTF-8"?>
    <svg width="\(size)" height="\(size)" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="bgGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#1f2937" />
                <stop offset="100%" stop-color="#111827" />
            </linearGradient>
        </defs>
        <rect x="0" y="0" width="1024" height="1024" rx="\(Int(squircleRadius))" fill="url(#bgGradient)" />
        <rect x="\(Int(G.body.x))" y="\(Int(G.body.y))" width="\(Int(G.body.w))" height="\(Int(G.body.h))" rx="\(Int(G.body.r))" fill="#f9fafb" />
        <g fill="#1f2937" fill-opacity="0.92">
            <circle cx="\(Int(G.ring.cx))" cy="\(Int(G.ring.cy))" r="\(Int(G.ring.r))" fill="none" stroke="#1f2937" stroke-opacity="0.92" stroke-width="\(Int(G.ring.stroke))" />
            <circle cx="\(Int(G.dotLeft.cx))" cy="\(Int(G.dotLeft.cy))" r="\(Int(G.dotLeft.r))" />
            <circle cx="\(Int(G.dotRight.cx))" cy="\(Int(G.dotRight.cy))" r="\(Int(G.dotRight.r))" />
            <rect x="\(Int(G.volumePill.x))" y="\(Int(G.volumePill.y))" width="\(Int(G.volumePill.w))" height="\(Int(G.volumePill.h))" rx="\(Int(G.volumePill.r))" />
        </g>
    </svg>
    """
}

func render(size: Int) -> NSBitmapImageRep {
    let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: size, pixelsHigh: size,
                               bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true,
                               isPlanar: false, colorSpaceName: .deviceRGB,
                               bytesPerRow: 0, bitsPerPixel: 0)!
    NSGraphicsContext.saveGraphicsState()
    let context = NSGraphicsContext(bitmapImageRep: rep)!
    context.imageInterpolation = .high
    NSGraphicsContext.current = context
    context.cgContext.scaleBy(x: CGFloat(size) / canvas, y: CGFloat(size) / canvas)
    drawIcon()
    context.flushGraphics()
    NSGraphicsContext.restoreGraphicsState()
    return rep
}

func writePNG(_ rep: NSBitmapImageRep, to path: String) {
    let data = rep.representation(using: .png, properties: [:])!
    try! data.write(to: URL(fileURLWithPath: path))
    print("wrote \(path)")
}

let args = CommandLine.arguments
if args.count > 1 {
    writePNG(render(size: 1024), to: args[1])
} else {
    let resources = "AppleTVRemoteApp/Sources/Atmo/Resources"
    let iconset = "\(resources)/RemoteHelp.iconset"
    let sizes = [("icon_16x16.png", 16), ("icon_16x16@2x.png", 32),
                 ("icon_32x32.png", 32), ("icon_32x32@2x.png", 64),
                 ("icon_128x128.png", 128), ("icon_128x128@2x.png", 256),
                 ("icon_256x256.png", 256), ("icon_256x256@2x.png", 512),
                 ("icon_512x512.png", 512), ("icon_512x512@2x.png", 1024)]
    for (name, size) in sizes {
        writePNG(render(size: size), to: "\(iconset)/\(name)")
    }

    let iconutil = Process()
    iconutil.executableURL = URL(fileURLWithPath: "/usr/bin/iconutil")
    iconutil.arguments = ["-c", "icns", iconset, "-o", "\(resources)/RemoteHelp.icns"]
    try! iconutil.run()
    iconutil.waitUntilExit()
    guard iconutil.terminationStatus == 0 else { fatalError("iconutil failed") }
    print("wrote \(resources)/RemoteHelp.icns")

    // Web + in-app SVGs share the exact geometry of the rendered icon
    for path in ["\(resources)/RemoteHelpIcon.svg",
                 "docs/assets/images/RemoteHelpIcon.svg",
                 "docs/assets/images/favicon.svg"] {
        try! (svg(size: path.hasSuffix("favicon.svg") ? 32 : 512) + "\n")
            .write(toFile: path, atomically: true, encoding: .utf8)
        print("wrote \(path)")
    }
}

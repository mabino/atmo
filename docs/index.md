---
layout: default
title: Home
description: A beautiful macOS SwiftUI application for discovering and controlling Apple TV devices
---

<section class="hero">
  <div class="container">
    <h1>Atmo</h1>
    <p>A beautiful macOS application for discovering and controlling Apple TV devices with an elegant SwiftUI interface and Python bridge.</p>
    <a href="https://github.com/mabino/atmo" class="btn" target="_blank">
      <i class="fab fa-github"></i>
      Get Started on GitHub
    </a>
  </div>
</section>

<section id="features" class="section">
  <div class="container">
    <h2>Features</h2>

    <div class="features-grid">
      <div class="feature-card">
        <div class="feature-icon">
          <i class="fas fa-search"></i>
        </div>
        <h4>Device Discovery</h4>
        <p>Automatically discover Apple TV devices on your local network with zero configuration required.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">
          <i class="fas fa-link"></i>
        </div>
        <h4>Seamless Pairing</h4>
        <p>Secure pairing with Apple TV devices using industry-standard protocols and credential management.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">
          <i class="fas fa-gamepad"></i>
        </div>
        <h4>Remote Control</h4>
        <p>Full remote control functionality with intuitive buttons and keyboard shortcuts for all Apple TV operations.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">
          <i class="fas fa-power-off"></i>
        </div>
        <h4>Power Management</h4>
        <p>Control power states of your Apple TV devices directly from the macOS interface.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">
          <i class="fas fa-code"></i>
        </div>
        <h4>Modern Architecture</h4>
        <p>Built with SwiftUI and Swift Concurrency, featuring a clean separation between UI and Python bridge.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">
          <i class="fas fa-print"></i>
        </div>
        <h4>Device Reports</h4>
        <p>Generate detailed reports of discovered devices with all identifiers, services, and connection details.</p>
      </div>
    </div>
  </div>
</section>

<section class="section screenshots">
  <div class="container">
    <h2>Screenshots</h2>

    <div class="screenshot-grid">
      <div class="screenshot">
        <img src="{{ '/screenshots/main-interface.png' | relative_url }}" alt="Main Interface" />
        <h4>Main Interface</h4>
        <p>Clean, modern interface showing discovered and paired Apple TV devices.</p>
      </div>

      <div class="screenshot">
        <img src="{{ '/screenshots/remote-control.png' | relative_url }}" alt="Remote Control" />
        <h4>Remote Control</h4>
        <p>Intuitive remote control interface with all essential Apple TV functions.</p>
      </div>

      <div class="screenshot">
        <img src="{{ '/screenshots/remote-menu.png' | relative_url }}" alt="Menu Options" />
        <h4>Menu & Options</h4>
        <p>Access to device reports and additional configuration options.</p>
      </div>
    </div>
  </div>
</section>

<section id="architecture" class="section architecture">
  <div class="container">
    <h2>Architecture</h2>

    <div class="arch-diagram">
      <h3>System Overview</h3>
      <p>Atmo uses a sophisticated architecture combining SwiftUI with a Python bridge to provide seamless Apple TV control.</p>
    </div>

    <div class="features-grid">
      <div class="feature-card">
        <h4>SwiftUI Frontend</h4>
        <p>Modern macOS application built with SwiftUI, featuring clean UI components and native macOS integration.</p>
        <ul>
          <li>ContentView - Main UI container</li>
          <li>BridgeViewModel - State management</li>
          <li>BridgeService - Python bridge communication</li>
        </ul>
      </div>

      <div class="feature-card">
        <h4>Python Bridge</h4>
        <p>Embedded Python environment using pyatv library for Apple TV communication and control.</p>
        <ul>
          <li>CLI interface with JSON output</li>
          <li>Device discovery and pairing</li>
          <li>Remote control commands</li>
          <li>Power management</li>
        </ul>
      </div>

      <div class="feature-card">
        <h4>Communication</h4>
        <p>Robust inter-process communication between Swift and Python components.</p>
        <ul>
          <li>JSON-based messaging</li>
          <li>Asynchronous operations</li>
          <li>Error handling and logging</li>
          <li>Process lifecycle management</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section id="getting-started" class="section getting-started">
  <div class="container">
    <h2>Getting Started</h2>

    <div class="steps">
      <div class="step">
        <div class="step-number">1</div>
        <div>
          <h3>Install Python Dependencies</h3>
          <p>Set up the Python virtual environment and install required packages.</p>
          <div class="code-block">
            <code>cd AppleTVRemoteApp
python3 -m venv ../.venv
../.venv/bin/pip install pyatv
bash Scripts/package_python.sh</code>
          </div>
        </div>
      </div>

      <div class="step">
        <div class="step-number">2</div>
        <div>
          <h3>Build and Run the App</h3>
          <p>Compile the SwiftUI application and launch it.</p>
          <div class="code-block">
            <code>xcrun swift build
xcrun swift run Atmo</code>
          </div>
        </div>
      </div>

      <div class="step">
        <div class="step-number">3</div>
        <div>
          <h3>Discover and Pair</h3>
          <p>Open the app, discover your Apple TV, and complete the pairing process.</p>
          <p>The app will automatically scan your network for Apple TV devices. Click on a discovered device and use the Pair button to establish a secure connection.</p>
        </div>
      </div>

      <div class="step">
        <div class="step-number">4</div>
        <div>
          <h3>Start Controlling</h3>
          <p>Use the remote control interface to navigate and control your Apple TV.</p>
          <p>Enjoy full remote control functionality with an elegant macOS interface!</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section id="docs" class="section">
  <div class="container">
    <h2>Documentation</h2>

    <div class="features-grid">
      <div class="feature-card">
        <h4><i class="fas fa-book"></i> Prerequisites</h4>
        <p>Complete development setup guide including macOS requirements, Python environment, and tooling.</p>
        <a href="{{ '/docs/prerequisites/' | relative_url }}" class="btn btn-ghost">Read More</a>
      </div>

      <div class="feature-card">
        <h4><i class="fas fa-code"></i> pyatv API Notes</h4>
        <p>Detailed notes on the pyatv library integration, discovery, pairing, and control interfaces.</p>
        <a href="{{ '/docs/pyatv_api_notes/' | relative_url }}" class="btn btn-ghost">Read More</a>
      </div>

      <div class="feature-card">
        <h4><i class="fab fa-github"></i> Source Code</h4>
        <p>Explore the complete source code on GitHub with comprehensive documentation and examples.</p>
        <a href="https://github.com/mabino/atmo" class="btn btn-ghost" target="_blank">View Repository</a>
      </div>
    </div>
  </div>
</section>
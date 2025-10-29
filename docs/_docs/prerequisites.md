---
layout: default
title: Prerequisites
description: Complete development setup guide for Atmo
---

<section class="section">
  <div class="container">
    <h1>Development Prerequisites</h1>

    <div class="content">
      <h2>macOS Requirements</h2>
      <ul>
        <li>macOS 13 Ventura or later</li>
        <li>Xcode 16+ with command-line tools installed (<code>xcode-select --install</code>)</li>
        <li>Swift toolchain that supports SwiftUI for macOS (bundled with Xcode)</li>
      </ul>

      <h2>Python Environment</h2>
      <ul>
        <li>Python 3.9.6 (matches <code>pybridge/python-version.txt</code>)</li>
        <li>Local virtual environment located at <code>.venv</code></li>
      </ul>

      <h3>Setting up Python Environment</h3>
      <p>Align the environment with the locked dependency set:</p>

      <div class="code-block">
        <code>python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install --requirement pybridge/requirements.lock</code>
      </div>

      <p>Install local test tooling (not bundled in the runtime lockfile):</p>

      <div class="code-block">
        <code>.venv/bin/pip install pytest</code>
      </div>

      <p>Run the Python test suite via the interpreter so the repository root stays on <code>sys.path</code>:</p>

      <div class="code-block">
        <code>.venv/bin/python -m pytest tests</code>
      </div>

      <p>If <code>.venv</code> already exists, remove it first (<code>rm -rf .venv</code>) or rerun the <code>pip install --requirement</code> step to sync with the lockfile.</p>

      <h2>Additional Tools</h2>
      <ul>
        <li><code>pytest</code> (to be installed when Python bridge tests are added)</li>
        <li><code>xcodebuild</code> available on PATH for CI/test automation</li>
      </ul>
    </div>
  </div>
</section>
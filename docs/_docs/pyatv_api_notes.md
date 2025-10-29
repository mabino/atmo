---
layout: default
title: pyatv API Notes
description: Detailed notes on pyatv library integration for Atmo
---

<section class="section">
  <div class="container">
    <h1>pyatv API Notes</h1>

    <div class="content">
      <p><em>Sources: <a href="https://pyatv.dev" target="_blank">pyatv.dev</a> documentation (Development → Scan, Pair and Connect / Control / Power Management sections).</em></p>

      <h2>Discovery & Scan</h2>
      <ul>
        <li><code>pyatv.scan(loop, timeout=5)</code> returns a list of <code>AppleTV</code> configuration entries.</li>
        <li>Each entry exposes identifiers accessible via <code>config.identifier</code>, <code>config.address</code>, etc.</li>
        <li>Discovery requires an asyncio loop.</li>
      </ul>

      <h2>Pairing Workflow</h2>
      <ul>
        <li>Pairing for each protocol is mandatory (Companion, AirPlay, RAOP) as noted in docs.</li>
        <li>CLI example <code>atvremote --id &lt;id&gt; --protocol airplay pair</code> prompts for PIN displayed on Apple TV.</li>
        <li>After pairing, credentials are stored automatically on disk using file-based storage (<code>pyatv.storage</code>), removing the need to re-supply credentials manually.</li>
        <li>Programmatic equivalent uses <code>pyatv.pair(config, protocol)</code> and asynchronous APIs to drive pairing and exchange PIN codes.</li>
      </ul>

      <h2>Remote Control Interface</h2>
      <ul>
        <li>Acquire via <code>atv = await pyatv.connect(config, loop)</code> then <code>remote = atv.remote_control</code>.</li>
        <li>Supported commands relevant to this app:</li>
        <ul>
          <li>Navigation: <code>remote.up(action=InputAction.SingleTap)</code>, <code>.down</code>, <code>.left</code>, <code>.right</code>.</li>
          <li>Selection: <code>remote.select()</code>, <code>remote.menu()</code>, <code>remote.home()</code>.</li>
          <li>Playback: <code>remote.play_pause()</code> to toggle playback state.</li>
        </ul>
        <li>Input actions default to <code>InputAction.SingleTap</code>; hold/double tap options available if needed.</li>
      </ul>

      <h2>Power Management Interface</h2>
      <ul>
        <li>Access with <code>power = atv.power</code> after connecting.</li>
        <li>Provides <code>await power.turn_on()</code> and <code>await power.turn_off()</code> for tvOS devices.</li>
        <li>Current power state available via <code>await power.power_state()</code> (returns <code>PowerState</code> enum).</li>
      </ul>

      <h2>Connection Lifecycle</h2>
      <ul>
        <li>Always close the connection via <code>atv.close()</code> in a <code>finally</code> block.</li>
        <li>Use <code>asyncio.run</code> or event loop management to bridge from synchronous entry points.</li>
      </ul>

      <h2>Credential Storage</h2>
      <ul>
        <li>Default file storage used by bundled tools lives at <code>$HOME/.pyatv.conf</code>; use <code>FileStorage.default_storage(loop)</code> to share credentials with pyatv CLIs.</li>
        <li>Credentials and other settings are automatically persisted after successful pairing when storage is provided and <code>storage.save()</code> is called.</li>
        <li><code>print_settings</code> command (and analogous APIs) expose saved credentials for debugging.</li>
      </ul>

      <p>These notes inform the Python bridge CLI implementation and bridging contract with the Swift UI app.</p>
    </div>
  </div>
</section>
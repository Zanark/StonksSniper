# Development and verification

## Local commands

From `C:\devdesk\homedesk\StonksSniper`, after the README setup:

```powershell
& .\.venv\Scripts\python.exe -m pytest -q
& .\.venv\Scripts\python.exe -m ruff check .
& .\.venv\Scripts\python.exe -m ruff format --check .
& .\.venv\Scripts\python.exe -m mypy
```

The tests use explicitly synthetic arithmetic fixtures and injected providers;
these never become application market observations. Desktop tests use an owned
offscreen QApplication, not an existing user window. They cover causal replay,
worker-thread success/failure, closing during an owned fetch, dataset identity,
parameter invalidation, export contents and insufficient history.

Opt-in live provider checks:

```powershell
& .\.venv\Scripts\python.exe .\scripts\check_live_data.py
```

Add `--render` followed by an absolute PNG path for an owned offscreen native
window. This makes real network requests, runs all seven patterns per dataset
and records a screenshot locally; it does not publish market observations.
The Windows offscreen plugin needs an explicitly loaded installed Segoe UI font.
The normal Windows application uses the same style and font.

## Initial verification evidence - 2026-11-11

- 37 tests passed. Ruff checks/formatting and strict source mypy passed.
- Actual Yahoo requests admitted 494 completed daily bars for `RELIANCE.NS`,
  494 for `TCS.NS` and 492 for `TCS.BO`, covering 2024-11-11 through
  2026-11-09. All seven variants ran on each dataset: 21 live-data simulations.
- `500325.BO` failed symbol/history resolution. `RELIANCE.BO` returned only a
  current-day bar, leaving no admissible completed observations. Both remained
  explicit failures; `TCS.BO` was separately selected for representative BSE
  verification, not used as a fallback for a RELIANCE request.
- Upstream yfinance/pandas deprecation warnings were observed. They are not
  evidence of failed retrieval and have not been hidden in application code.
- The initial offscreen render exposed missing glyphs: that Qt platform had no
  discovered fonts. The verification script now loads installed Segoe UI before
  rendering. The real-data 1600x1150 image was inspected: controls, provenance,
  charts, explanations and fill ledger are readable. Source links use the
  readable accent rather than the default dark-blue hyperlink color.
- Separate TCS requests produced materially different body-engulfing results.
  A same-process BSE pair matched all 492 bars/targets. Three fresh-process
  BSE requests then differed in 203-210 bars, with adjusted OHLC differences
  up to about INR 0.001 and 15-22 changed target states. Near-equal body boundaries
  crossed the variant's exact comparison thresholds. The application preserves
  supplied prices rather than silently rounding them to hide sensitivity.
  Provider-side origin/precision remains unqualified. SS-07 tracks qualification;
  SS-10 tracks immutable study storage. Export exact inputs before comparing runs.

These are technical observations, not independent market-data reconciliation,
exchange-calendar qualification, a Windows installer test, human acceptance or
publication approval. Current adjusted history may revise between requests.

## ELI15 redesign verification - 2026-11-11

- Seven plain-language lessons and 74 dictionary entries provide a meaning plus
  vegetables/toys/household examples. The pattern button, highlighted-word hover
  and dictionary search share authored content; no runtime model or API key is needed.
- Final validation: 47 tests passed; Ruff lint/format and strict source mypy passed.
  Tests send an actual local pointer event and Tab/Return key events rather than
  emitting the navigation signal. Merely positioning a text cursor inside a link
  does not establish keyboard link focus; the test now uses ordinary Tab navigation.
- For each of the seven rules, the chart at a 50-day replay prefix matches the
  same rule drawn from an actually truncated dataset. Changing only the drawing
  window preserves the result, metrics and full-prefix running high.
- Motion is optional; disabling it stops replay and native transitions. Repeated
  replay/render tests caught a native area-series crash: the boundary line now has
  an explicit parent. Reset stops animation before deleting series and old axes.
- A worker-failure test hung in Qt's test wait with logging capture. Pumping owned
  events with a short Python sleep preserves logging and checks captured failures;
  neither application exceptions nor pytest logging were disabled.
- Actual native screenshots exposed invisible logo pixels, dark primary buttons
  and deferred old chart labels. Explicit Qt SVG rendering validates/paints the
  logo, narrower stylesheet selectors preserve action backgrounds, and the capture
  harness flushes deferred deletion before recording a chart.
- The final gallery run admitted RELIANCE.NS=494, TCS.NS=494 and TCS.BO=492
  completed daily observations, running seven variants per dataset. Its six images
  use RELIANCE.NS fetched at 2026-11-11T22:35:01.012284+05:30, with observation
  dates 2024-11-11 through 2026-11-09. Counts/dates are provider observations,
  not independently reconciled market truth.
- Inspected 1440x900 screenshots cover price, money, rule, pattern and dictionary;
  the 1366x768 image verifies the compact main workspace. The script asserts the
  actual window size, preventing an oversized window from masquerading as compact.
  Long text panels may still scroll. Animation is disabled for deterministic captures.

Reproduce the gallery with actual network retrieval:

```powershell
& .\.venv\Scripts\python.exe .\scripts\check_live_data.py --gallery C:\devdesk\homedesk\StonksSniper\docs\images
```

`docs\images\captures.json` records screenshot provenance, not raw observations.
README is image-led, with an explanatory caption for each view. Shared-machine
checks used only independently owned offscreen instances; no existing user
application was controlled. Human comprehension, normal Windows/DPI, installer
acceptance and independent feed reconciliation remain unverified. Provider
adjustments may revise and upstream deprecation warnings remain visible.

## First-prototype publication

The user separately authorized commit, push and a GitHub release on 2026-11-11.
The published v0.1.0 prerelease is an early-access Python package, not a standalone Windows
installer. README embeds six actual-data native screenshots with captions.

Build the wheel after installing the declared development dependencies:

```powershell
& .\.venv\Scripts\python.exe -m build --wheel --outdir dist
Get-FileHash .\dist\stonks_sniper-0.1.0-py3-none-any.whl -Algorithm SHA256
```

The first build attempt exposed a missing `build` module. Added it to the
development extra and installed that missing tool; the declared setuptools
backend was resolved in the build tool's isolated environment.

The resulting wheel was installed without dependencies into a separate owned
target. Its module path was checked to exclude the editable source checkout;
native offscreen startup, logo rendering, packaged theme notice, seven-rule
inventory and 74-entry dictionary succeeded. This reuses existing runtime
dependencies, not a clean-machine test. No existing user app was driven.
Generated wheels/checksums stay ignored and are release attachments, not source
files. SS-11 retains the standalone Windows, clean-profile and human gates.

## Stock-download loading screen - 2026-11-11

The supplied GIF is a single packaged asset also embedded by README. A stacked
in-window loading page shows the captured stock/exchange while the existing
worker runs; its shared completion handler stops the movie and restores the
tabs after success or failure. There is no artificial wait or invented progress.
The header's Animations switch also pauses/resumes the GIF, without starting it
while idle or changing retrieval.

Six desktop and ten learning tests passed, plus Ruff lint/format and strict
source mypy. Controlled worker tests check real frame advancement, disabled
motion, toggles, captured request identity and both completion paths.
A separately installed wheel imported outside the source tree and contained
the exact source GIF: 30 frames with infinite looping. Its 1366x768 native loading
view was inspected using a blocked test provider, not downloaded or fabricated
market observations. Only owned offscreen instances were used.

The candidate was built outside the existing release outputs. The published
v0.1.0 wheel and checksum remain unchanged; this follow-up is available in source,
not retroactively in that release. These checks do not qualify a clean Windows
machine, DPI scaling or human acceptance.

## Explicit GitHub tracking adoption

`TODO\tracking.json` identifies the public repository, dedicated Project 14,
actual Status options, stable workstream IDs, remote identities and last
verified baselines. Numbered workstreams own managed issue descriptions;
`00_INDEX.todo` and `99_DEVELOPMENT_LEDGER.todo` are excluded.

Use the approved credential runner from the locally installed development
manual when available. It scopes credentials to the child command; never put
tokens in commands, source, issue bodies or chat.

Preview, with no writes:

```powershell
python "C:\devdesk\homedesk\skill-library\skills\development-documentation-manual\scripts\with_github_token.py" -- python .\scripts\sync_tracking.py
```

Apply an inspected preview:

```powershell
python "C:\devdesk\homedesk\skill-library\skills\development-documentation-manual\scripts\with_github_token.py" -- python .\scripts\sync_tracking.py --apply
```

`--only SS-01` restricts either operation to one pilot workstream. A different
machine without that runner needs its own authorized `gh` authentication;
the repository does not distribute credentials.

Status mapping: `NOT_STARTED` -> open/Todo, `IN_PROGRESS` -> open/In Progress,
`DONE` -> closed with completed reason/Done. Technical completion does not mean
human approval. Update Tasks, Completion evidence and Completion log together.

Stable markers recover an interrupted issue creation; mappings are saved
atomically. Unexpected remote body/title/state/Project changes stop the sync
instead of being overwritten. Preserve comments and reconcile conflicts
explicitly. Read-after-write verification retries bounded reads only because
Project field changes may become visible after mutation acknowledgement.
An API error or exhausted read bound remains a failure, never a successful sync.
All original 18 mappings were applied and read back; subsequent full applies retained
the original issue and Project item identities. A GitHub HTTP 503 interrupted
one rerun, which stopped explicitly; the next rerun verified every mapping.
The ELI15 redesign added SS-19 as issue #19 with a Project 14 item. Its final full
apply verified all 19 bodies, states, memberships, statuses and local backlinks:
SS-01 through SS-05 and SS-19 are closed-completed/Done; SS-06 through SS-18 remain
open/Todo. Original issue/Project identities were retained.

No automatic schedule, GitHub Action, order execution or deployment is enabled.
Issue/Project writes do not authorize Git commits, pushes or release publication.

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

## Scope logo follow-up - 2026-11-11

The subsequent logo follow-up replaces the original rising line with five
green/red candles seen through a circular scope and pale crosshairs. The shared
SVG is used by the app icon/header and README. Actual Qt icon renders were
inspected at 42, 88 and 256px; no existing user instance was restarted. Earlier
gallery screenshots and the published v0.1.0 package retain their original logo.

## Square-corner styling follow-up - 2026-11-11

Rectangular GUI surfaces use square corners throughout the shared stylesheet:
cards, inputs, buttons, tabs, inspector panes, list selections, sliders,
checkboxes and scrollbars. Native chart backgrounds also have zero roundness;
the shared logo's tile and candle rectangles are square, while its scope remains
circular. Keep this consistent when adding controls.

Sixteen desktop/learning tests, Ruff lint/format and strict source mypy passed.
All four tabs and the loading surface were inspected in an owned 1366x768
offscreen window; all four chart backgrounds were checked. No market data was
retrieved or generated and no existing user instance was driven. Prior gallery
screenshots and the published v0.1.0 package remain unchanged.

## Circular animated brand and GIF-led README - 2026-11-12

The original animation starts with a rectangular green/coral candle chart.
Its gold reticle darts across all four quadrants, settles in the center, fires
a visible bullet and flashes on impact. The scene then cuts to a circular logo
with transparent surroundings. The matching static SVG has its reticle centered.
This is decorative branding, not market observations or a recommendation.
README displays the GIF at 352px (previously 88px); gold-and-green vector image
buttons link to setup, the written guide and the frozen prototype download.
Application window/taskbar icons use the matching still SVG, and the header uses
the packaged GIF. **Animations** pauses it and shows the centered still; reenabling
restores the movie, and accepted close stops it.
The existing DeepSeaFoam GUI and square rectangular surfaces remain unchanged.

Pillow is a development-only media dependency. Reproduce the original artwork:

```powershell
& .\.venv\Scripts\python.exe .\scripts\build_presentation.py --brand
```

Reproduce the native GIF demos with explicit real network retrieval:

```powershell
& .\.venv\Scripts\python.exe .\scripts\build_presentation.py --gallery --end 2026-11-09
```

The initial latest-range request failed the existing price validation on
2026-11-11: prices must be finite and positive. No invalid row was dropped and
no observations were substituted. A separate explicitly bounded request through
2026-11-09 succeeded with 493 actual RELIANCE.NS observations starting 2024-11-12.
The provider's precise reason for the invalid row is unverified. GIF provenance
records the requested end, actual observation dates, fetch time and provider
warnings; these historical demos are not a claim of latest-price qualification.

Five 1366x768 GIFs show native replay of the final 60 completed sessions plus
lesson/dictionary navigation. Frames are sampled deterministically, not presented
as real-time screen recordings. Inspected first/last frames for every demo and
search/lock/bullet/impact/circular-finish branding frames plus native still icons.
The supplied Stonks GIF remains embedded and used for downloads.

Fifty-one tests, Ruff lint/format and strict source mypy passed. Desktop tests
check actual logo frame advancement, rectangle-to-circle transparency, native
still clipping, motion-off stability, still-image substitution, resume and close
cleanup. All 70 frames decode through Qt. Visual inspection exposed Qt ignoring
the SVG clip path: explicit painter clips now keep searching arms inside the
rectangle and the final logo/icon entirely inside the circle. An initial asset
test incorrectly used full-size coordinates on the 46px header image; corrected
the test to decode the full-size asset independently.
A separately built/installed candidate
imports outside the source checkout and contains byte-identical logo SVG/GIF
and loading GIF; motion and transparency worked there. It reuses existing runtime
dependencies, not a clean-machine qualification. The published v0.1.0 wheel and
checksum remain unchanged. No existing user instance was driven or restarted.

### Equal-size square-to-circle cut

The search chart is now square. Its outer side equals the final circle's outer
diameter, including both gold borders and native painter clipping. The grid and
seeded search cover the taller square; shot timing and the centered still remain
unchanged. Regenerated the shared app/README GIF without fetching market data.
The existing GUI demos need no recapture because their centered still is unchanged.

The geometry regression failed against the old 332x244px search stage. The updated
70-frame GIF keeps the same 328x328px visible bounds throughout, including the final
circle. Inspected full-size first/final frames side by side. Eight desktop tests
and targeted Ruff lint/format checks passed. Published v0.1.0 remains unchanged;
no existing user app was driven or restarted.

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

# Development and verification

## First public release: v1.0.0

The November 23 public-release milestone includes the complete current learning
desk: 27 strategies/demos, date-range simulations, the book companion, Market
tools and Python headless lab. Versioned Windows metadata, source/notices and
README downloads use v1.0.0; older v0.x releases remain historical prereleases.
The workflow derives output paths from `stonks_sniper.__version__`, not an old
hardcoded prototype directory. The pinned Windows dependency baseline is unchanged.

Release qualification requires the exact source SHA, a clean build receipt,
hosted Windows/Linux checks, actual provider/frozen runtime checks and published
asset read-back. The Windows application remains unsigned. Local Application
Control restrictions, clean-machine/DPI and human acceptance are not overridden
by successful hosted checks. Earlier development evidence below is historical;
v1.0.0 includes the features previously described as source-only.

Published [v1.0.0](https://github.com/Zanark/StonksSniper/releases/tag/v1.0.0)
as the latest stable release at `883c941a4b721b190368da60906677ca745c48e5`.
The [exact-source live run 45155983942](https://github.com/Zanark/StonksSniper/actions/runs/45155983942)
passed Linux/Python 3.11 and Windows/Python 3.13.14, including actual NSE/BSE
provider cases and the Windows frozen runtime. That EXE fetched 494 HDFCBANK
observations through November 20, exercised all 27 strategies and all 27
date-range simulation routes, and exported its exact experiment.

All six published assets were downloaded again and matched the qualified
originals byte for byte; the five manifest payloads matched SHA-256 checksums.
Verified all 33 first-party build-input hashes against the tagged Git source,
allowing only exact LF-to-CRLF checkout conversion for text files. The notices
archive contains 330 metadata/license entries. The public EXE's PE metadata
reports 1.0.0, and anonymous executable/source-archive URLs returned HTTP 200.
The attached Python wheel imported outside the source checkout and exposed all
27 headless strategies. Existing v0.x tags/assets and this host's security
controls were not changed. These checks do not qualify local frozen execution
on this Application-Control-restricted machine or promise reproducible binary bytes.

## Pointer-led README walkthroughs - 2026-11-23

The five November 12 product GIFs have been refreshed, with six additional tours:
independent Simulate, lesson-linked real-market demos, The Intelligent Investor,
Market tools, paper orders/holdings and manual risk/options labs. All eleven use
the current native interface. Decorative logo/meme animations, application code
and immutable v1.0.0 release assets are unchanged.

The normal ICICIBANK/NSE fetch worker supplied **494 actual completed observations,
2024-11-25 through 2026-11-20**. The requested end was November 23; its potentially
incomplete current-day bar was excluded normally. No profitable rule/date search,
fictional market prices or fallback ticker was used. The full-range EMA example
and Donchian learning demo lose money; the shorter date-range example gains.
Paper order results retain costs and their loss; manual scenarios stay labelled.

The capture process owns an offscreen QApplication and separate Yahoo cache.
Qt mouse/keyboard events actually operate visible buttons, tabs, lists, dropdowns,
editors and sliders. The pointer and expanding click rings are rendered overlays,
not an OS mouse recording. Owned dialogs are centered over the dimmed owned parent;
captions add 76 pixels to the 1366x768 native canvas. Replay is accelerated and
animations are disabled; no existing user window, pointer or application is driven.
Caption holds scale with word count, with a longer pause for the book practical.

Recreate **review candidates**, using the declared development dependencies:

```powershell
& .\.venv\Scripts\python.exe .\scripts\build_presentation.py --gallery --gallery-dir C:\devdesk\homedesk\StonksSniper\build\readme-walkthrough-candidate
```

This makes an actual network request. Review the candidates before replacing
`docs\images` media. `--end YYYY-MM-DD` explicitly bounds the request; fresh
provider history/adjustments and the default lookback can change future captures.
This is a repeatable capture procedure, not a byte-reproducible market dataset.
`--brand` is separate and is not required for a product-tour refresh.

[`gif-captures.json`](images/gif-captures.json) records source/fetch/session dates,
warnings, price basis, application version, source commit/dirty flag, capture-script
SHA-256 and per-clip actions, dimensions, timings, bytes and SHA-256. `frames` counts
composited inputs; `encoded_frames` accounts for identical frames merged by GIF
encoding without losing duration. Each clip is bounded to 180 input frames and
less than 10 MB. These eleven total **5,844,000 bytes**, with loops of 11-31 seconds.

Every encoded frame decoded at 1366x844, with matching total timing and hashes.
Inspected two contact sheets and native-size simulation, monthly-purchase,
paper-pending and click-effect details; final output was compared with those
inspected views. This is native-image inspection, not browser/DPI or human approval.
Four focused native interaction/safety regressions join the full offline gate:
**361 passed, 4 opt-in live cases skipped**, normal exit; Ruff lint/format and
strict source mypy passed. The separate actual provider/capture run also completed.

The first candidate caught two capture assumptions, not product defects: a native
dropdown briefly ignores releases after opening, and an empty workbook correctly
refuses calculation instead of producing a report. The harness now waits for popup
activation and demonstrates that refusal. Windows also retained SQLite handles
until worker-process exit; a parent now cleans only its own temporary cache after
that exit. No dependency or security-policy change was needed.
Visible-platform capture is rejected before any application window is constructed.

Published the refreshed README/media at
[`fd438e2`](https://github.com/Zanark/StonksSniper/commit/fd438e2dfdd250c97f4884735c198803a919b430).
Anonymous raw README, receipt and all eleven GIFs returned HTTP 200 and matched
the committed blobs exactly. Binary files also match their local receipts.
Text checkout differences and the script hash were checked against exact Git
bytes or the exact LF-to-CRLF variant, not arbitrary normalization. No release
asset was replaced or uploaded.

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
window. This makes real network requests, runs all registered patterns per dataset
and records a screenshot locally; it does not publish market observations.
The Windows offscreen plugin needs an explicitly loaded installed Segoe UI font.
The normal Windows application uses the same style and font.

## Kite-inspired market tools

November 23 source-native qualification: **357 passed, 4 opt-in live cases
skipped**, normal process exit. Ruff lint/format, strict mypy and Git whitespace
passed. New focused cases cover average-cost/fee P&L, opening-only fills, gap
stops, activated persistent stop limits, explicit expiry/rejection/cancellation,
clock ordering, comparison alignment, weekly-year boundaries, close crossings,
risk/payoff arithmetic, malformed watchlists, save refusal and native workflows.

Actual new Yahoo requests returned **496 observations each for ICICIBANK.NS
and TCS.NS, 2024-11-21 through 2026-11-20**. Both captured native watchlists,
common-session comparison, charts/studies/annotations, alert inspection,
paper buys/partial sales and final marked reporting passed. A hand-directed
two-unit ICICIBANK example realised a small loss on its partial sale; its
remaining 1.5 units were left marked, not forced sold. This is a workflow check,
not an optimized strategy or efficacy test.

Inspected owned native charts, order ledger, watchlist, relative comparison,
manual scenarios and guide at 1366x900/1366x768. The second pass reused the
preserved actual snapshots rather than fetching again. Fixed unstyled integer
controls, clarified drawing inputs, exposed complete cell text via tooltips,
removed stale queued-status wording and made numeric sorting explicit when
quotes are missing. No existing app window/process or environment was altered.

Watchlist identifiers and full paper evidence export explicitly; existing files
are refused. Evidence exports contain future captured observations beyond the
revealed cursor and cannot resume the paper account. Twenty original tool
lessons are shared with Dictionary. [Coverage, formulas, sources and boundaries](market-tools.md).
These additions are included in v1.0.0, not the historical v0.3.0 release.
Normal Windows/DPI/human acceptance, live depth, broker fills and profitability
are not established by these checks.

## Real-market demos and headless agent lab

Latest-source verification on November 21: **322 offline tests passed,
4 opt-in live tests skipped**, normal exit; Ruff lint/format and strict mypy passed.
New tests cover all 27 lesson routes/causal rule measurements, independent
Explore/workbook state, event navigation, fetch failure/close guards, book
history exercises, custom/reference signal equivalence and causal prefixes,
JSON validation, costs/capital/date slicing, receipts and refusal to overwrite.

Actual closed-market ICICIBANK fetched through the new headless command:
**496 observations, 2024-11-21 through 2026-11-20**. Ran all 27 built-ins on
the same saved input/costs and hypothetical INR 100,000, plus both shipped custom
examples; custom SMA/Donchian targets, fills and equity matched their built-ins.
The test interval produced **15 positive and 12 negative** strategy returns;
no losing example was replaced. These counts are not efficacy or selection advice.

Owned source-native checks also exercised all 27 learning demos, four book
history exercises and an actual current ICICIBANK reference-worker request,
automatic worksheet calculation and financial-sector guards. Inspected actual
rule/explanation, monthly-purchase and workbook views at 1366x768. Persistent
rule axes avoid stale overlapping labels during replay; no user window was driven.

The [skill](../.github/skills/stonks-sniper-lab/SKILL.md) was discovered enabled
by Copilot CLI as a repository skill. The local canonical skills directory was
also registered with `copilot skill add`; discovery from outside this checkout
verified the same enabled skill as a custom source, not a stale personal copy.
Other hosts still require their own discovery or explicit Markdown loading.
The documented actual custom-rule command
also returned a saved JSON receipt. These are source-native checks, not a new
frozen EXE qualification, normal-DPI/human acceptance or profitability proof.
The historical v0.3.0 EXE remains unchanged; v1.0.0 includes the desktop features
and Python lab. [Interface and contracts](agent-lab.md).

## Intelligent Investor companion and closed-market study

The latest source adds separate technical/book learning sections, original
notes mapped to 20 main chapters, a current fundamental workbook and arithmetic
exercises. [Coverage, formulas and source receipts](intelligent-investor.md).
The published v0.3.0 remains unchanged and does not contain this companion.

November 21 verification: **269 offline tests passed, 4 live cases skipped**,
normal exit; Ruff lint/format, strict mypy and Git whitespace checks passed.
The new cases cover independent valuation/margin/net-net arithmetic, missing
or invalid facts, sector applicability, currency/unit/provenance handling,
weekend/holiday/after-hours history and native book/worker/export behavior.
An initial native crash exposed release of worker ownership before thread-local
cleanup finished; waiting for the finished thread before dropping references
fixed it. Both success/failure and close-during-fetch cases then passed.

Actual Saturday ICICIBANK history/fundamental requests succeeded. An owned
source-native 1366x768 diagnostic exercised **both real UI fetch workers**,
loaded **496** observations through **2026-11-20**, ran all 27 technical
strategies and exported an actual current fundamental worksheet. Inspected
the chapter and workbook views. ICICIBANK was classified as financial-sector,
with industrial screens disabled and missing facts preserved, not fabricated.
The committed opt-in ICICIBANK test independently passed every strategy.
An actual Yahoo status read at 20:11 IST explicitly returned `CLOSED`.
Upstream yfinance/pandas deprecation warnings remain visible, not mistaken
for failed fetching. No dependency changes, user-window control or new release.

Run the ICICIBANK network regression explicitly:

```powershell
$env:STONKS_LIVE_TESTS = "1"
& .\.venv\Scripts\python.exe -m pytest -q tests\test_live_provider.py -k ICICIBANK
Remove-Item Env:\STONKS_LIVE_TESTS
```

Snapshot fetch timestamps are not financial-statement publication dates.
The workbook never feeds current fundamentals into historical backtests.
Other sectors, complete earnings/dividend histories, audited reconciliation,
normal Windows/DPI interaction and human acceptance are not implied.

## Separate date-range simulation

The **Simulate** window, included in v0.3.0, reuses the existing engine without changing
strategy rules or accounting. It filters the loaded observations before running:
inclusive dates, fresh cash, in-range warmup and no pre-start holdings. Persistent
price/trade/money series reveal only the current prefix. Each window captures its
own dataset/settings and owns its timer; parent close and reduced motion stop it.

Twelve new desktop regression cases cover launch and independence, inclusive
intervals, future-data hiding, independently calculated gain/loss/flat and
cash-only outcomes, completed-sale costs, invalid/empty ranges, actual timer
playback, pause, step, finish, restart and close. Final full offline verification:
**220 passed, 3 opt-in live tests skipped**, normal process exit; Ruff lint/format,
strict source mypy and Git whitespace checks passed. The new twentieth
workstream also required updating the existing tracking inventory regression.

An owned offscreen check fetched actual HDFCBANK/NSE history: 493 observations
with the dated missing-row warning retained. All 27 strategies ran through the
new window on 444 observations from 2025-01-10 to 2026-10-27. Verified prefix and
final graphs/ledger, plus timer-driven completion for SMA. Inspected native
price/money views at 1160x768 and main controls at 1366x768 without controlling
a user-owned window.

These November 12 checks were source-native, not a qualification of the
v0.2.0 executable, normal Windows/DPI interaction or human acceptance. That
release is unchanged and does not contain this feature. v0.3.0 has a separate
release qualification described below. Final holdings remain
marked, not automatically sold; see [the guide](guide.md#simulate-your-own-dates).

## Windows executable: v0.3.0

The November 21 request authorizes a new immutable prototype containing all
changes through the date-range Simulate window. Version 0.3.0 retains the pinned
v0.2.0 runtime/build dependencies. Its live frozen diagnostic additionally
opens Simulate for all 27 strategies, selects dates, checks the initial hidden
future prefix, reaches the final graph/ledger/P&L and closes each owned window.
[Exact-source live CI 44911765905](https://github.com/Zanark/StonksSniper/actions/runs/44911765905)
passed Windows and Linux on `6ece40ef50f71959fa7889993f267d0248bdf0f6`.
The actual frozen Windows EXE fetched 496 HDFCBANK observations, exercised all
27 strategies and all 27 selected-date simulation windows, and exported.
Local offline tests passed 220 cases with 3 opt-in live cases skipped; separate
actual HDFCBANK source-native checks, lint/format and strict mypy passed.

Published [v0.3.0](https://github.com/Zanark/StonksSniper/releases/tag/v0.3.0)
at that exact clean built source. All four uploaded assets were downloaded again
and matched the qualified CI bytes. Verified all manifest hashes, all 24 source
inputs (including the documented LICENSE CRLF checkout conversion) and the
330-entry notices archive. The tag and public release metadata were read back.
Older tags/assets stay unchanged. Signing, local Application Control, normal
DPI and human acceptance remain separate.

## Tests and Windows executable: v0.2.0

`.github/workflows/tests.yml` runs offline regression tests, Ruff lint/format and
strict source mypy on Linux/Python 3.11 and Windows/Python 3.13. Actions are pinned
to verified commit IDs and receive read-only repository permissions. Windows also
builds the executable and runs its native-plugin diagnostic before retaining
the candidate as an Actions artifact. These artifacts are not GitHub releases.

The first hosted run passed Windows tests, actual provider checks and the frozen
native diagnostic. Linux completed 208 tests, then Python 3.11 aborted during
interpreter finalization with `none_dealloc`. Qt tests now retain one
session-owned QApplication and explicitly deliver deferred deletions after each
test; `processEvents()` alone does not drain `deleteLater()` outside an event
loop. The updated local suite passed all 211 tests, including actual downloads.
The second manual run again passed Windows, including the actual frozen
diagnostic, but failed during Python 3.11 finalization. A later source-identity
check showed that dispatch still targeted the original `af2fa53`, so it did not
qualify the subsequent Qt cleanup change. An
[independent reduced reproduction](https://github.com/optiland/optiland/issues/1069)
identifies PySide6 6.12 singleton-reference corruption on Python 3.11, with links
to Qt's binding issue; [superqt applies the same compatibility bound](https://github.com/pyapp-kit/superqt/blob/main/pyproject.toml).
Dependencies now select PySide6 below 6.12 only on Python
3.11; Python 3.12+ and the pinned Windows build retain their existing versions.
Revisit that temporary bound only after corrected wheels pass the complete suite
with normal interpreter exit. The compatibility run on `6ca68ba` resolved
PySide6 6.11.3, exposing two newer-only `QDate(date)` overloads during type
checking before Linux tests could run. Date controls now use the stable explicit
year/month/day constructor without changing the selected dates. The subsequent
compatibility runs are recorded below. An assertion-pass summary does not
override a nonzero process exit.

Run `43119611661` then passed the complete Linux/Python 3.11 suite and actual
provider checks with a normal exit. Windows caught a one-unit RGB difference
between the checked-in ICO and native Qt rendering. That comparison now allows
one 8-bit RGB quantization unit while retaining exact alpha, all seven sizes
and transparent/opaque boundary checks. No artwork or application behavior was
changed.

The final [live run 43120473704](https://github.com/Zanark/StonksSniper/actions/runs/43120473704)
passed both platforms on exact source
`9284b00bc9647f65c76bf81d96e2d79cef1cdbb6`, including normal Linux process exit
and the actual Windows frozen diagnostic. That executable fetched 493 usable
HDFCBANK observations, retained the missing-row warning, simulated all 27
strategies and exported the experiment. The final actual local full suite
also passed 211 tests, plus Ruff lint/format and strict source mypy.

Published [v0.2.0](https://github.com/Zanark/StonksSniper/releases/tag/v0.2.0)
as a separate prerelease at that exact tested source; v0.1.0 is unchanged.
Downloaded all four published assets again and verified byte-for-byte equality
with the qualified CI artifacts. The three manifest-listed checksums, clean
source receipt, all 24 build inputs and 330-entry notices archive passed
verification. LICENSE alone uses CRLF in the hosted checkout versus LF locally;
that exact conversion matches the recorded input hash, and the bundled license
matches the receipt byte for byte. Input hashes describe build-checkout bytes,
not universal cross-checkout line endings or bit-for-bit reproducible binaries.
The executable is unsigned; hosted success does not override this machine's
Application Control restriction or qualify clean-machine/DPI/human acceptance.

Yahoo availability must not make every pull request nondeterministic. Live tests
are opt-in, locally or through **Run workflow / live_provider** on trusted `main`:

```powershell
$env:STONKS_LIVE_TESTS = '1'
& .\.venv\Scripts\python.exe -m pytest tests\test_live_provider.py -q
Remove-Item Env:\STONKS_LIVE_TESTS
```

These actually download HDFCBANK/NSE, RELIANCE/NSE and TCS/BSE and simulate every
registered strategy. The manual workflow also fetches real HDFCBANK history
through the frozen executable's native worker and exercises all rules/export.
No failed request is replaced with fixtures or another ticker.

### Isolated Windows x64 build

Build with Python 3.13.14 on Windows x64. Keep existing application environments
and windows untouched. The published dependency baseline is pinned in
`packaging\windows-requirements.txt`; use a new build environment:

```powershell
& .\.venv\Scripts\python.exe -m venv build\windows-1.0.0\venv
& .\build\windows-1.0.0\venv\Scripts\python.exe -m pip install -e '.[packaging]' -r packaging\windows-requirements.txt
& .\build\windows-1.0.0\venv\Scripts\python.exe scripts\build_windows.py
```

Output: `C:\devdesk\homedesk\StonksSniper\dist\windows-v1.0.0`.
The builder refuses an existing output directory; use `--output` with a fresh
candidate path for another build. It creates a single-file, windowed EXE with
the glass ICO, package assets, Qt plugins/chart libraries, timezone/TLS data,
license notices, exact dependency/input receipt and SHA-256 checksums.
It collects named packages/assets, never the whole checkout or a user profile.
No API tokens or market observations are included.

The Windows build is GPL-3.0-only because **Qt Charts is GPLv3/commercial, not
LGPL**. See [notices](../packaging/THIRD_PARTY_NOTICES.md) and
[corresponding source](../packaging/SOURCES.md). This is not a commercial Qt build.

### Exercise the actual EXE

From an owned test shell, use a fresh report filename:

```powershell
$exe = 'C:\devdesk\homedesk\StonksSniper\dist\windows-v1.0.0\StonksSniper-1.0.0-windows-x64.exe'
$report = Join-Path $env:TEMP 'stonks-frozen-smoke.json'
$env:QT_QPA_PLATFORM = 'windows'
$process = Start-Process -FilePath $exe -ArgumentList @('--smoke-test', "`"$report`"", '--live') -PassThru
if (-not $process.WaitForExit(180000)) { Stop-Process -Id $process.Id; throw 'Diagnostic timed out' }
if ($process.ExitCode -ne 0) { throw "Diagnostic failed: $($process.ExitCode)" }
Get-Content -LiteralPath $report
```

Without `--live`, the diagnostic checks assets, native initialization and lessons
without making market-data requests. With it, it uses an isolated Yahoo cache,
the normal fetch worker, all 27 strategy/UI paths and the real JSON-export slot.
It writes a report, owned-window screenshot and exact experiment beside the
report; these private test outputs are not release assets. The diagnostic window
is never shown onscreen and its animations are deliberately off. That is not
human visual acceptance or qualification of interactive animation behavior.
No user-owned window, process or environment is driven, restarted or upgraded.

### HDFCBANK regression evidence

Reproduced the reported request over 2024-11-12 through 2026-11-12: Yahoo supplied
494 adjusted rows, with all four adjusted prices `NaN` on November 11.
An unadjusted request confirmed that day's raw close and adjusted close were
missing. Excluding only completely missing adjusted OHLC rows leaves **493**
usable HDFCBANK/NSE observations through November 9 and emits a dated warning
in logs, the Data panel and export. No interpolation, price-basis switch or
weakened Candle validation was introduced. All-unusable and partially corrupt
responses still fail.

Three new missing-price regressions failed before the fix and passed afterward.
The full local suite including the three opt-in live cases passed **211 tests**;
Ruff lint/format and strict source mypy passed. The native Windows source
diagnostic fetched HDFCBANK, exercised 27 rules and exported its exact inputs.
An initial diagnostic rapidly queued animated chart redraws and crashed during
cleanup; deterministic diagnostics now disable motion and drain events between
rules. Interactive animation stress qualification remains open.

The first live suite also exposed only one usable observation for HDFCBANK/BSE;
that did not qualify an all-strategy run. The explicit representative BSE check
is TCS/BSE (491 usable observations), not an undisclosed ticker fallback.
Provider completeness, independent price reconciliation, clean-machine/DPI
qualification, signing and human acceptance remain open under SS-07/SS-11.

The local candidate EXE built successfully, with 329 third-party metadata/license
entries in its notices archive. Its attempted standalone launch from an external
Unicode folder was blocked before Python initialized: Windows Application Control
refused the extracted `python313.dll`. The owned error process was closed; no
policy was disabled, changed or bypassed. Therefore local frozen runtime,
Unicode-path runtime and clean-machine qualification are **not verified**.
The source-native live test above did pass. The release gate instead requires
the requested hosted Windows workflow's frozen diagnostic to pass, using an
ordinary pinned Python distribution and no host Python paths.

## Twenty-strategy expansion - 2026-11-12

The current source has 27 usable rules, 27 authored lessons and 97 dictionary
entries. [The strategy catalogue](strategies.md) records all 20 added variants'
formulas, thresholds, warmups, references, everyday examples and failure modes.
The original seven keep their ordering and behavior.

`studies.py` computes added-rule decisions and chart guides together. Nested
EMAs preserve leading unavailable values, each stage waits for a complete seed,
and shared EMA logic also serves the original EMA/MACD rules. Ichimoku draws
only cloud values calculated 26 observations earlier. Chandelier's documented
app-specific ratchet resets after an exit; unavailable exit-line segments are
not joined across cash periods. No intraday stop fill is fabricated.

Hand-calculated references exercise all 20 indicators, with additional checks
of shifted cloud values, gap-aware ranges, Wilder/nested seeds, directional
gates, ties, entry/retain/exit conditions and degenerate-volume conventions.
Every added rule can enter and exit on labelled arithmetic fixtures. Every
prefix preserves targets and guides; engine equity/benchmark/trades also
preserve prefixes. Native tests select all 20 new rules, open their lessons and
dictionary entries, verify actual indicator series and export their exact
rule/source metadata. Longer warmups no longer run against insufficient
fixed-length test prefixes.

An initial new UI assertion used the wrong widget name; it failed explicitly
and was corrected to the actual exact-rules browser. Final full suite:
**201 passed**, Ruff lint/format and strict source mypy passed. Owned offscreen
1366x768 views were inspected with synthetic arithmetic data, not presented as
real market screenshots. Long library labels wrap in the existing narrow pane.
No existing user window was driven or restarted. Fresh live-data reconciliation,
human comprehension, normal Windows/DPI and installer qualification remain
separate; the old release and historical GIFs were not regenerated.

## Complete strategy reference - 2026-11-12

The linked [strategy reference](strategies.md) now explains all 27 implemented
rules, including the original seven, in actual picker order. Every entry has
an ELI15 idea, exact buy/sell/retain conditions, calculation and warmup,
illustrative numeric walkthrough, failure modes and educational source.
The catalogue table identifies stable keys and required signal inputs.

The source audit covered `patterns.py`, `studies.py`, the existing lessons and
`engine.py`. It distinguishes strict/inclusive boundaries, state retention,
EMA/Wilder seeds, previous-only Donchian ranges, shifted cloud values and the
app-specific Chandelier ratchet and Ultimate midpoint rule. Shared instructions
explain next-opening execution, all-cash sizing, fractional research units,
fees/slippage, benchmark timing and unsold final holdings.

Documentation checks matched all 27 names, keys, order, minimum histories and
source URLs to the actual catalogue; checked explanation coverage, local links
and section anchors; and checked the illustrative arithmetic. These are source
and documentation checks, not a new runtime test run, fresh data qualification,
performance evidence or human acceptance. README remains image-led and links
to the full reference. The strategy-documentation work itself changes no runtime,
asset, dependency or frozen-release content.
SS-06 remains in progress for its broader research and configuration work.

## Clear glass and consistent static icons - 2026-11-12

The user rejected the square GIF's glass appearance: broad gradients collapsed
into a jagged opaque patch when reduced to the exact approved palette.
A new regression reproduced the hidden grid before regeneration. The GIF now
uses thin reflection contours over a clear chart, retaining every approved
visible color, transparent circular finish, constant bounds and 2.56-second morph.
The still SVG has lighter tint/vignetting and a curved specular reflection.

The shared centered still is rendered at seven native icon sizes:
16, 24, 32, 48, 64, 128 and 256px. The generated, packaged `logo.ico` contains
pixel-identical renders for Windows/browser use. Application and window icons
share the helper; the header remains static. README's new PNG cover composites
the same still with the existing regular Times New Roman banner. The generator
explicitly loads the installed font when rendering that cover offscreen.
GitHub's own browser favicon and Windows pinned-shortcut caches are not controlled
by the README or this native icon helper.

Final targeted desktop/learning checks: **62 passed**; Ruff lint/format,
strict source mypy and diff checks passed. Checks include a clear background and
visible grid, all-frame palette/clarity, equal-size transparent rounding, static
header and exact ICO/native equality at every size. Inspected before/after
decoded states, the actual SVG/native icons, a new empty offscreen native window
and the cover at its authored resolution.

A no-isolation wheel build failed explicitly because setuptools was absent from
the local environment. The ordinary isolated build then resolved the declared
backend without changing the app environment. Its wheel contains the exact
SVG/GIF/ICO; an extracted candidate imported outside the editable source and
confirmed shared static app/window icons using existing dependencies.
This is not a clean-machine or normal Windows-shell/DPI qualification.
The frozen v0.1.0 wheel checksum is unchanged. No market retrieval, gallery
recapture, actual-user-window control or automatic restart was performed.

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

### Graph-paper buttons and serif title

The three README buttons follow the user's double-outline reference, with a
subtle edge glow and uniform 14x14-unit square grids. Gold/seafoam outlines retain
the requested money palette. Button labels and the project-title banner now use
Times New Roman, with Times/serif fallbacks where unavailable. No font files are
copied or embedded.

Inspected actual native SVG renders of the banner and every button at authored
300px and README 260px widths. Windows resolved installed Times New Roman; labels
fit within both frames. Ruff lint/format passed. Navigation targets, app theme,
logo geometry and existing GUI demos are unchanged. This is native SVG inspection,
not a claim of full browser or all-platform font qualification.

### Exact palette and always-static app header

The latest user direction supersedes the earlier gold/green palette and animated
app header. The app header/window icon now always render the centered static SVG;
Animations still controls chart/replay/loading motion, never the header. The
README retains the search/shot animation and matching size; the later refinement
below replaces the original 70-frame abrupt cut.

All authored banner/button/logo colors follow the exact six-color contract in
`ui-design.md`; red/green candlesticks are the only drawing exception. Removed
off-palette gradients. A raster inspection caught adaptive GIF encoding shifting
the requested background color. The logo now uses a fixed indexed palette,
including the permitted candle red, while actual GUI demos keep their existing
shared adaptive palette. The new regression checks every visible logo-GIF color
in every frame and SVG paint colors with the candle exception restricted to its
group. Chart interiors remain opaque; the final outside remains transparent.

Native preview also revealed the earlier comma-separated SVG font-family list
rendered as sans-serif despite Times New Roman being installed. Explicitly naming
the single Times New Roman family fixes the actual rendered artwork. The user's
later refinement sets the title and button labels to regular weight, not bold. Inspected
serif title/button renders at authored and README widths. This corrects the
earlier insufficient font-availability check; it is not all-platform qualification.
Hosts without the font may substitute; no font files are copied or embedded.
The banner and visible application title/header use the exact **Stonks Sniper**
case and space; repository/package identifiers remain unchanged.

Fifty-two tests, Ruff lint/format and strict source mypy passed. The static-header
regression rejected the former animated header; the palette regression rejected
the previous artwork. Recaptured all five native 1366x768 GIF demos using 493
actual RELIANCE.NS observations through the explicit 2026-11-09 cutoff, with fresh
provenance. Their first/last header regions match. Exact study prices can change
between provider requests; these are not immutable inputs or latest-price checks.
Inspected the final palette, search/bullet/circular finish, native static header
and serif artwork. The supplied meme and historical still gallery are unchanged.
No existing user instance was driven/restarted; published v0.1.0 is unchanged.

### Slow, smooth square-to-circle transition

The user rejected the hard cut. The shape and explicit native painter clip now
share a continuous corner radius, with 96 authored steps over 3.84 seconds.
Quintic easing starts and ends with zero speed and acceleration; the reticle,
candles and full grid remain stationary. The inner border gradually appears.
Square side and final circle diameter still match in every decoded frame.

The new regression failed against the old abrupt-cut asset (zero intermediate
silhouettes). The new GIF decodes as 155 frames, with 84 distinct intermediate
silhouettes spanning 3.80 seconds, within the full 3.84-second transition.
It checks duration, monotonic corner removal, bounded changes between frames,
constant bounds and transparent final corners. The full loop is 10.36 seconds;
identical frames are merged by GIF encoding without losing their timing.

### Glass scope and 1.5x faster rounding

The subsequent request adds original blue-tinted lens shading, a dark optical
edge, curved reflections and a layered rim to the shared SVG and README GIF.
Reference photographs informed the effect; neither photo is copied or published.
Gradient stops use only the six approved colors. Fixed-palette encoding retains
only those colors plus candle red. Inspected both encodings: rejected noisy
Floyd-Steinberg dithering and kept the clean, deliberately simpler GIF shading.
The native static SVG retains smooth shading; the header remains static.

The 96-sample quintic morph now takes exactly 2.56 seconds, down from 3.84.
GIF delays use 10ms ticks, so 30/30/20ms groups distribute the time exactly;
easing uses cumulative elapsed time. Search, lock, bullet, impact and final hold
durations are unchanged. The final asset decodes as 159 frames, with 84 distinct
intermediate silhouettes spanning 2.40 seconds and a 9.08-second complete loop.
Constant bounds, monotonic rounding and transparent corners remain checked.

New rendered-glass and faster-timing assertions rejected the old flat/slow
artwork before generation. Ten desktop tests, Ruff lint/format, strict source
mypy and diff checks passed. Inspected decoded search/lock/morph/final states and
the native static render; no gallery recapture, network market request, external
texture, dependency installation or existing-user-window control was performed.
The frozen v0.1.0 wheel remains byte-identical. This is not human approval or
fresh normal-Windows/DPI/installer qualification.

### GIF-only final-circle glass and finishing shimmer

The square and morph now have no glass reflections or optical rim. Glass appears
only on the completed circle, followed by one eased 1.2-second blue/white sweep
and a 0.6-second still finish. The 2.56-second morph and 9.08-second loop remain.
Static SVG, ICO, native icons and README cover are byte-identical to the previous
milestone.

The new timing regression first failed against the previous GIF. An initial
sweep touched antialiased edge pixels; the silhouette checks caught it. Bounding
the reflection inside the lens fixed that without relaxing those checks.
All 63 desktop/learning tests, Ruff lint/format and diff checks passed.
Inspected seven decoded square/morph/glass/shimmer/finish states. This is not
human visual approval. No gallery recapture, market retrieval, user-window
control, dependency change or replacement of the frozen release was needed.

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

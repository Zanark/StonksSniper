# Run Stonks Sniper

[Back to the GIF tour](../README.md) | [Simple guide](guide.md)

## Windows executable: no Python required

Open [v1.0.0, the first public release](https://github.com/Zanark/StonksSniper/releases/tag/v1.0.0).
Download `StonksSniper-1.0.0-windows-x64.exe` and double-click it from a writable
folder. It is a standalone Windows x64 application, not an installer; no Python
or administrator install is required. First launch extracts the bundled runtime
to a temporary directory, so allow a little extra startup time.

The executable is **unsigned**. Windows/browser security may warn or block it;
checksums do not establish publisher trust. Do not disable your security tools.
Internet access is needed for unofficial Yahoo history, not for reading lessons.
Download the notices ZIP, `build-info.json` and `SHA256SUMS.txt` for dependency,
license and integrity information. The application is GPLv3 because it uses
GPLv3 Qt Charts; [corresponding source and rebuild instructions](../packaging/SOURCES.md)
accompany the release.

## Source: Windows and Python 3.11+

v1.0.0 includes date-range **Simulate**, all 27 learning demos, the Intelligent
Investor companion and the **Market tools** desk. The Python package also
supports the [headless agent lab](agent-lab.md); the Windows EXE is GUI-only.
No API token is needed for the initial Yahoo connection.

```powershell
git clone https://github.com/Zanark/StonksSniper.git C:\devdesk\homedesk\StonksSniper
Set-Location C:\devdesk\homedesk\StonksSniper
git switch --detach v1.0.0
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -e .
& .\.venv\Scripts\python.exe -m stonks_sniper
```

The detached tag selects this exact release; use `main` for ongoing development.
Already cloned? Fetch tags and select the release without discarding local work.
On later launches:

```powershell
& C:\devdesk\homedesk\StonksSniper\.venv\Scripts\python.exe -m stonks_sniper
```

## First experiment

1. Enter `RELIANCE` with **NSE**, or `TCS` with **BSE**, then **Load stock**.
2. Choose an idea. **Explain pattern** teaches what it does with an everyday example.
3. After changing an idea or cost, click **Test idea**.
4. **Play days** replays history. **Save results** exports the complete experiment,
   including the exact prices, rather than only the day currently visible.
5. **Simulate** opens a separate window: choose dates inside
   the loaded history, then **Start simulation** to watch buys/sells and the money
   chart. The final result shows profit/loss in INR and percent.
   [Date boundaries, warmup and unsold stock](guide.md#simulate-your-own-dates).
6. **Market tools -> Capture Explore history** opens the same observations for
   manual chart/order practice. Start with **Tool guide** to learn each control.

**Animations** pauses the loading GIF, chart transitions and both kinds of replay.
The application header is always static.
The README GIFs are separate files: GitHub does not expose an in-README pause
switch. Open the linked written guide if you prefer no motion.

## Missing provider prices

Yahoo sometimes returns a session with no adjusted OHLC prices, as observed for
`HDFCBANK.NS` on November 11, 2026. Such rows are excluded, **not repaired or
filled**. The Data panel and exported experiment preserve a dated warning;
the headline displays the last usable observation, not an invented latest price.
Calculations use the remaining observations, so gaps can affect strategy results.
Partial invalid prices, bad volume and inconsistent OHLC still fail validation.
If no usable completed observations remain, loading still fails explicitly.
The pandas deprecation warnings printed by yfinance are separate from that error.

## Historical prototype

[v0.1.0 downloads](https://github.com/Zanark/StonksSniper/releases/tag/v0.1.0)
include a Python wheel and source, **not a standalone Windows installer**.
That frozen release predates the current branding, extra strategies and missing-price fix.
Use v1.0.0 or the latest source instead. v0.2.0/v0.3.0 remain historical
Windows prereleases and omit the newer companion, demos and tools desk.
Do not mix the released wheel with a different same-version build.

## Development and media tools

For contributors only:

```powershell
& .\.venv\Scripts\python.exe -m pip install -e '.[dev]'
```

Pillow is a development-only GIF authoring dependency, not an application runtime
dependency. [Development commands and evidence](development.md).

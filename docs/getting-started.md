# Run StonksSniper

[Back to the GIF tour](../README.md) | [Simple guide](guide.md)

## Latest source: Windows and Python 3.11+

The latest source includes the circular animated logo, square-cornered interface
and stock-download GIF. No API token is needed for the initial Yahoo connection.

```powershell
git clone https://github.com/Zanark/StonksSniper.git C:\devdesk\homedesk\StonksSniper
Set-Location C:\devdesk\homedesk\StonksSniper
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -e .
& .\.venv\Scripts\python.exe -m stonks_sniper
```

Already cloned? Update your checkout first without discarding local work.
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

**Animations** pauses the logo, loading GIF, chart transitions and replay.
The README GIFs are separate files: GitHub does not expose an in-README pause
switch. Open the linked written guide if you prefer no motion.

## Published prototype

[v0.1.0 downloads](https://github.com/Zanark/StonksSniper/releases/tag/v0.1.0)
include a Python wheel and source, **not a standalone Windows installer**.
That frozen release predates the loading GIF, circular logo and square-corner
follow-ups. Use the latest source above for the interface in the GIF tour.
Do not mix the released wheel with a different same-version build.

## Development and media tools

For contributors only:

```powershell
& .\.venv\Scripts\python.exe -m pip install -e '.[dev]'
```

Pillow is a development-only GIF authoring dependency, not an application runtime
dependency. [Development commands and evidence](development.md).

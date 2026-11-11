# Indian market-data research and integration register

Research date: 2026-11-11. Scope: a personal, local NSE/BSE learning simulator.
This is a dated candidate register, not a claim to enumerate every provider or
certify exchange authorization. No broker account, paid subscription or production
token was used. Recheck all prices, terms and entitlements before integration.

## Recommendation

**Start:** Yahoo Finance via yfinance, explicitly unofficial and personal-research
only, for daily NSE (`.NS`) and BSE (`.BO`) observations. Its project documentation
says it is not affiliated with or vetted by Yahoo and points users to Yahoo terms.
This is convenient free access, not an SLA, accuracy guarantee, redistribution
license or supported Yahoo developer product. The adapter rejects malformed data,
does not repair it and does not substitute other observations on failure.

**Upgrade shortlist:** Upstox, FYERS and Zerodha for a documented broker-backed
daily/intraday adapter; Dhan and Angel One are additional high-priority candidates.
Choose only after verifying the user's account entitlement, historical ranges,
corporate-action semantics and actual NSE/BSE instrument coverage. A trading API
being free does not imply free historical market data.

**Authoritative daily-file path:** investigate NSE/BSE bhavcopies and action files
as a separate ingestion/reconciliation source. A daily file covers many instruments,
not a ready-made per-stock adjusted history. Exchange publication does not grant
blanket redistribution rights. Do not bypass site access controls or silently
scrape protected endpoints.

**Licensed vendor path:** request personal desktop/API quotations from TrueData,
Global Datafeeds and Accelpix when feed quality, depth or historical coverage
outgrows the free path. Marketing claims remain claims until independently
qualified and contractual permissions are checked.

## Detailed first-priority comparison

| Candidate | Verified documentation / advertised access | Important integration questions | Backlog |
|---|---|---|---|
| Yahoo/yfinance | Project documents personal research and unofficial status; daily history supports explicit auto-adjust controls | Yahoo terms, throttling, revisions, incomplete sessions, symbol identity, adjustment quality; NSE/BSE live checks are separate | SS-03, SS-14 |
| Upstox V3 | Bearer-token endpoint; minutes 1-300, hours 1-5, daily/weekly/monthly. Docs list daily history from Jan 2000, minute/hour from Jan 2022. Daily request limit one decade, small-minute requests one month | Account/app login and token expiry; active instrument history differs from expired derivatives; Plus entitlement for expired-instrument APIs; adjustment and BSE coverage must be tested | SS-12 |
| Zerodha Kite Connect | Historical candles with instrument tokens and minute through daily intervals. Official product page lists Connect at INR 500/month for history and streaming; free Personal tier lists order/portfolio features, not these feeds | Token/session lifecycle, instrument-master expiry, current pricing/taxes, exchange entitlement, action adjustments. Continuous expired futures documented, not a universal expired-options archive | SS-12 |
| FYERS | Official page advertises free Trading API and separate Standard/Prime quotas: Standard 5,000/day, 50/min, 5/sec; Prime 500,000/day, 500/min, 10/sec at research time. Daily depth listed 5 years vs 25+ years | Do not assume one "free API" has Prime depth or quotas. Validate plan-specific history, sockets, BSE instruments and current fee terms | SS-12 |
| DhanHQ V2 | Daily `/charts/historical`; token authentication, exchange/security IDs, OHLCV arrays. Intraday docs list 1/5/15/25/60 minutes, last five years and up to 90 days/request | Data API subscription versus order API entitlement; advertised "back to inception" daily history needs instrument-level verification; exclusive daily `toDate`; timestamp/adjustment semantics | SS-13 |
| Angel One SmartAPI | Official portal retrieved but only its JavaScript shell was available to this research tool | Read actual historical-candle docs/SDK, TOTP/auth, lookback per interval, current charges, rate limits and data terms; none established by the shell | SS-13 |
| ICICI Direct Breeze | Readable docs specify NSE equity/F&O; explicitly say BSE and MCX unavailable. 100 calls/min and 5,000/day. App key, secret, session token, checksum and timestamp flow | NSE-only restriction makes it insufficient alone for NSE+BSE. Investigate historical intervals/depth and action handling; do not activate any order endpoints | SS-15 |
| Twelve Data | Official NSE and BSE exchange pages list EOD and minimum Grow/Venture plans at research time | Free Basic access is not established for Indian exchanges. Verify data credits, adjustments, symbols, personal-use licensing and current price | SS-17 |
| Alpha Vantage | Support FAQ lists 25 free requests/day (and application-based educational/open-source access); documents split/dividend adjustments | Verify specific NSE/BSE coverage and full-history entitlement rather than extrapolating global coverage. No key obtained | SS-17 |
| EODHD | Official docs provide exchange-list and ticker-discovery APIs requiring a token, with active/delisted modes | Call coverage discovery under an entitled account; establish exact NSE/BSE history, actions, revisions and plan limits before selecting | SS-17 |

These are documentation findings, not measurements of API availability or speed.
No performance/latency marketing claims are used to rank providers.

## Extended broker register

Each named option has an explicit investigation task in the linked workstream.
Portal discovery is not capability verification.

| Option | Evidence obtained this session | Required next investigation | Backlog |
|---|---|---|---|
| Shoonya / Finvasia | Official readable docs describe REST/WebSocket, OAuth2 and historical-candle section | Daily vs intraday depth/limits, fees, terms, new auth versus older Noren SDKs | SS-13 |
| Flattrade Pi | Official JavaScript portal identifies free API/live-feed offering | Read actual history API and current login, instrument and plan constraints | SS-13 |
| Alice Blue ANT | Readable official docs describe live feeds, app registration, app key/secret and current a3 base | Historical endpoint availability and retention; current API generation; fees | SS-13 |
| Kotak Neo | Official product page links official REST docs/Python SDK and advertises zero API charges | Historical data availability distinct from quotes, NSE/BSE coverage and session/TOTP flow | SS-15 |
| 5paisa Xstream | Official docs enumerate historical candles, quotes, socket, OAuth/access-token sections | Read history endpoint windows, tokens, plan costs, action basis and BSE coverage | SS-15 |
| IIFL Capital | Official developer portal retrieved as JavaScript shell | Current docs/API generation, XTS versus other products, history entitlement | SS-15 |
| Groww | Official SDK docs advertise history/live feeds, NSE/BSE/MCX and require account + active API subscription | Subscription fees, candle depth, auth, data terms and expired-history capability | SS-16 |
| Paytm Money | Official developer portal retrieved as JavaScript shell | Read supported market-data APIs, plan fees, historical availability and authentication | SS-16 |
| m.Stock | Official page advertises free trading/data APIs, real-time feed and historical OHLCV; links versioned docs | Verify API version, account requirements, NSE/BSE history, retention/quotas and terms | SS-16 |
| Samco Trade API | Official page advertises free APIs/live streaming and 30 years market-adjusted history, with account activation | Verify history claim per instrument, adjustment algorithm and download/retention rights | SS-16 |
| Mastertrust | Readable official docs show OAuth authorization-code flow, daily login/token handling and endpoint index | Do not assume historical candles from an order/profile API; locate market-data product/terms | SS-18 |
| Motilal Oswal | Search located vendor-named `motradingapi/PythonSDK`; guessed corporate landing pages returned 404 | Verify official ownership from a corporate link and current historical offering before adoption | SS-18 |
| Definedge | Guessed API landing page returned 404 | Discover current official API portal, eligibility, read-only history and terms | SS-18 |
| Pocketful | Guessed API landing page returned 404 | Discover current official portal, API generation and data entitlements | SS-18 |
| Jainam / Duck, Zebu / Mynt, other XTS brokers | Discovery candidates only; no primary capability evidence obtained | Establish official current product names/portals; do not assume common backend means identical history or licenses | SS-18 |

Do not treat the unverified/discovery rows as integrations or as claims that the
service currently offers suitable NSE/BSE candles. Add newly discovered providers
without renumbering existing workstream identities.

## Non-broker alternatives and rejected defaults

| Route | Finding / boundary | Backlog |
|---|---|---|
| NSE daily bhavcopy/UDiFF and corporate actions | Official reports and data-subscription pages timed out from this environment; schemas/terms not verified in this session | SS-14 |
| BSE daily bhavcopy/history and corporate actions | Official bhavcopy page could not be retrieved; current archive path/schema/rights unverified | SS-14 |
| Google Finance | Official disclaimer prohibits downloading/storing/reprocessing/redistributing data without prior written consent. No supported general-purpose Google Finance historical API was established. Do not scrape it as the app's default | SS-14 |
| TrueData | Official site advertises real-time/history and API developer use | Confirm exact exchange authorization, personal API plan, history, action handling and retention contract | SS-17 |
| Global Datafeeds | Official API page advertises NSE/BSE equities, derivatives, history/EOD/delayed/real-time and REST/WebSocket options | Obtain contract/quote, inspect pagination/history, investigate vendor continuity and adjustment basis | SS-17 |
| Accelpix | Official site advertises market-data APIs/history and exchange-authorized vendor status | Independently confirm authorization and current NSE/BSE product entitlement; measure gaps/revisions only with licensed data | SS-17 |
| Commercial enterprise feeds (LSEG, Bloomberg, FactSet, exchange-direct) | Future enterprise discovery, no access/prices/capabilities evaluated here | SS-17 |
| Community mirrors/packages (`nsepython`, `jugaad-data`, datasets) | Wrappers/mirrors are not original exchange licenses or provider guarantees | SS-14 |

## Adapter qualification checklist - applies to every option

1. Record a current official source, API version, review date and actual account
   entitlement. Verify NSE **and** BSE separately, including instrument/ISIN mapping.
2. Confirm personal local display, storage, export, derived data, model access and
   redistribution rights. Never publish raw downloaded datasets in this repository.
3. Establish nominal versus adjusted OHLC, volume adjustment, dividends/splits/
   bonuses/rights, delistings, symbol changes and historical revisions.
4. Test supported intervals, inclusive/exclusive boundaries, timezone, history
   depth, pagination, missing sessions, zero-volume bars, suspensions and circuits.
5. Measure rate-limit/error behaviour, retries/backoff and token/session expiry;
   never bypass a provider block. Do not equate retrieval success with correctness.
6. Reconcile representative symbols/dates/actions against permitted independent
   sources. Keep expected differences and unresolved discrepancies visible.
7. Assess secrets storage, minimum read-only scopes and callback handling. Broker
   integration must not add trading authority or require sharing secrets in chat.
8. Produce a documented go/no-go, cost, terms receipt, adapter tests, immutable
   observation snapshot and user-visible capability/freshness labels.

## Source receipts

Primary pages below were read on the research date unless labelled failed or
discovery-only. Provider-authored claims are not independently certified.

- yfinance status/terms: https://ranaroussi.github.io/yfinance/
- yfinance history reference: https://ranaroussi.github.io/yfinance/reference/api/yfinance.Ticker.history.html
- Upstox candles: https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/
- Upstox backtesting/expired entitlement: https://upstox.com/developer/api-documentation/backtesting/
- Kite historical data: https://kite.trade/docs/connect/v3/historical/
- Kite pricing (redirected official page): https://zerodha.com/products/api/
- FYERS offering and plan table: https://fyers.in/products/api/
- Dhan history: https://dhanhq.co/docs/v2/historical-data/
- Angel One portal (shell only): https://smartapi.angelone.in/docs
- Shoonya docs: https://shoonya.com/api-documentation
- Flattrade portal (shell only): https://pi.flattrade.in/docs
- Alice Blue docs: https://v2api.aliceblueonline.com/
- Breeze docs: https://api.icicidirect.com/breezeapi/documents/index.html
- Kotak Neo official page: https://www.kotakneo.com/platform/kotak-neo-trade-api/
- 5paisa docs: https://xstream.5paisa.com/dev-docs/
- IIFL portal (shell only): https://developers.iiflcapital.com/
- Groww SDK/eligibility: https://groww.in/trade-api/docs/python-sdk
- Paytm Money portal (shell only): https://developer.paytmmoney.com/
- m.Stock API offering: https://www.mstock.com/trading-api
- Samco offering: https://www.samco.in/tradeapi
- Mastertrust documentation: https://tradeapi.mastertrust.co.in/
- Motilal SDK (discovery-only ownership): https://github.com/motradingapi/PythonSDK
- NSE reports (fetch timed out): https://www.nseindia.com/all-reports
- NSE subscriptions (fetch timed out): https://www.nseindia.com/market-data/real-time-data-subscription
- BSE bhavcopy (transport failure): https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx
- Google Finance restrictions: https://www.google.com/googlefinance/disclaimer/
- Twelve Data NSE plan/delay: https://twelvedata.com/exchanges/xnse
- Twelve Data BSE in exchange listing: https://twelvedata.com/exchanges
- Alpha Vantage limits/adjustments: https://www.alphavantage.co/support/
- EODHD discovery: https://eodhd.com/financial-apis/exchanges-api-list-of-tickers-and-trading-hours
- TrueData: https://www.truedata.in/
- Global Datafeeds: https://globaldatafeeds.in/apis/
- Accelpix: https://accelpix.com/

The Twelve Data page displayed an unexpected Sunday-Thursday schedule for NSE;
do not adopt that calendar. This illustrates why provider metadata needs independent
validation rather than copying all fields from a marketing page.

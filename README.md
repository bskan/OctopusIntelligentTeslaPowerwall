# OctopusIntelligentTeslaPowerwall

A Python API server that automates Tesla Powerwall time-of-use tariff settings using Octopus Energy's planned dispatch slots.

## Overview

This project integrates Tesla Powerwall with Octopus Intelligent Dispatch by:

1. Fetching Octopus Energy planned dispatch slots via their GraphQL API
2. Generating a time-of-use tariff schedule that avoids charging during partner slots
3. Sending the updated TOU settings to your Tesla Powerwall via the Tesla Owner API

## Prerequisites

- Python 3.10+
- A Tesla account linked to your Powerwall
- An Octopus Energy account with Intelligent Dispatch enabled
- Your Octopus API key and account number

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
MYEMAIL=your_email@example.com
OCTOPUS_API_KEY=sk_live_YOUR_API_KEY_HERE
OCTOPUS_ACCOUNT_NUMBER=A-YOUR_ACCOUNT_NUMBER_HERE
```

| Variable | Description |
| --- | --- |
| `MYEMAIL` | Email address used for your Tesla SSO login |
| `OCTOPUS_API_KEY` | Octopus Energy GraphQL API key (from your account) |
| `OCTOPUS_ACCOUNT_NUMBER` | Your Octopus Energy account number |

`.env` is gitignored — never commit it.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### API Server

```bash
python -m iotesla
# or with custom port
python -m iotesla -p 8000 -h 0.0.0.0
```

Endpoints:

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `GET` | `/api/status` | Current configuration status |
| `POST` | `/api/tou-json` | Generate TOU JSON from startDt/endDt |
| `POST` | `/api/run` | Full pipeline: dedup, fetch slots, generate TOU, send to Tesla |
| `POST` | `/api/send` | Send an already-formed TOU JSON to Tesla |

Example `POST /api/run` body:

```json
{
    "startDt": "2024-01-15 23:30:00+00:00",
    "endDt": "2024-01-16 05:30:00+00:00"
}
```

Deduplication:

- If the incoming `startDt` matches `nextRunStart` in `latest.json`, the Octopus API is not called
- If the Octopus API returns the same `nextRunStart` as `latest.json`, the Tesla API is not called
- Skipped responses return `{"status": "skipped", "reason": "no_change"}` or `{"status": "skipped", "reason": "octopus_unchanged"}`

Home Assistant example:

```yaml
rest:
  - url: "http://iotesla:8000/api/run"
    method: POST
    payload: >
      {"startDt": "{{ states('sensor.octopus_intelligent_next_offpeak_start') }}", "endDt": "{{ states('sensor.octopus_intelligent_next_offpeak_end') }}"}
    payload_content_type: json
    content_type: "application/json"
```

### CLI

Run the full pipeline directly:

```bash
python iotesla.py
```

### Docker

```bash
docker build -t iotesla .
docker run --env-file .env iotesla
```

## How it works

1. `io.py` fetches your Octopus Energy planned dispatch slots and outputs JSON to stdout
2. `iotesla.py` reads that output, generates a TOU tariff JSON that excludes the partner slots, and sends it to your Tesla Powerwall
3. The Powerwall then avoids charging during those slots (allowing partner dispatches to happen)

## Files

| File | Purpose |
| --- | --- |
| `iotesla.py` | FastAPI server and main logic for TOU generation |
| `io.py` | Octopus Energy GraphQL API client |
| `cli.py` | Tesla Owner API CLI (from TeslaPy) |
| `gui.py` | Tesla device GUI (from TeslaPy) |
| `teslapy/` | TeslaPy library (from TeslaPy) |
| `.env` | Local configuration (gitignored) |
| `.env.example` | Configuration template |

## License

This project is based on [TeslaPy](https://github.com/tdorssers/TeslaPy) by Tim Dorssers.

TeslaPy is licensed under the Apache License 2.0.

## Disclaimer

This project interacts with unofficial Tesla and Octopus Energy APIs. Use at your own risk. I am not responsible for any issues with your Tesla Powerwall or Octopus Energy account.

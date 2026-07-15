# dlt Workshop Note: Logfire Region and Base URL

While working on the dlt workshop for the LLM Zoomcamp, I ran into a Logfire authentication issue caused by a region mismatch.

## Problem

I created a Logfire project in the **European Union** region and copied a **Write Token** from that project.

The token prefix looked like this:

```text
pylf_v1_eu_...
```

However, when running the local Python code, Logfire returned a `401 Unauthorized` error:

```text
Logfire API returned status code 401. Detail: Invalid token
Failed to export span batch code: 401, reason: Unauthorized
```

At first, it looked like the token was wrong or not loaded from `.env`.

## Root Cause

The token itself was valid, but the Logfire client was using the default Logfire endpoint, which points to the US region.

My token was created for the EU region, so the client needed to send telemetry to the EU Logfire API instead.

In other words:

```text
EU token + default US endpoint = 401 Invalid token
```

## Fix

Add the Logfire base URL that matches the region of the token.

For an EU Logfire project, add this to `.env`:

```bash
LOGFIRE_TOKEN=your_write_token_here
LOGFIRE_BASE_URL=https://logfire-eu.pydantic.dev
```

Then configure Logfire in Python:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(".env"), override=True)

import logfire

logfire.configure(
    token=os.getenv("LOGFIRE_TOKEN"),
    base_url=os.getenv("LOGFIRE_BASE_URL"),
)
```

After this change, telemetry was sent successfully to the correct Logfire project.

## Notes

If your token starts with:

```text
pylf_v1_eu_
```

use:

```text
https://logfire-eu.pydantic.dev
```

If your token belongs to the US region, use the default US endpoint.

The important part is that the **Logfire token region and base URL must match**.
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from logfire.experimental.query_client import LogfireQueryClient


load_dotenv(dotenv_path=Path(".env"), override=True)

read_token = os.getenv("LOGFIRE_READ_TOKEN")
base_url = os.getenv("LOGFIRE_BASE_URL")

client = LogfireQueryClient(
    read_token=read_token,
    base_url=base_url,
)

# This is the trace with tool calling that produced 5 spans
trace_id = "019f64dce012f377b9a3be99bbedb647"

sql = f"""
SELECT *
FROM records
WHERE trace_id = '{trace_id}'
ORDER BY start_timestamp
"""

result = client.query_json_rows(sql)
records = result["rows"]

print("records:", len(records))

print("\nFirst record keys:")
print(records[0].keys())

print("\nFirst record:")
print(json.dumps(records[0], indent=2)[:4000])
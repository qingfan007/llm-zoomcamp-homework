import os
from pathlib import Path

from dotenv import load_dotenv
from logfire.experimental.query_client import LogfireQueryClient


load_dotenv(dotenv_path=Path(".env"), override=True)

client = LogfireQueryClient(
    read_token=os.getenv("LOGFIRE_READ_TOKEN"),
    base_url=os.getenv("LOGFIRE_BASE_URL"),
)

trace_id = "019f64dce012f377b9a3be99bbedb647"

sql = f"""
SELECT
    span_name,
    message,
    attributes
FROM records
WHERE trace_id = '{trace_id}'
ORDER BY start_timestamp
"""

result = client.query_json_rows(sql)
records = result["rows"]

total_input_tokens = 0

for record in records:
    span_name = record["span_name"]
    message = record["message"]
    attributes = record.get("attributes") or {}

    print("\nSPAN:", span_name)
    print("MESSAGE:", message)
    print("ATTRIBUTE KEYS:", list(attributes.keys()))

    input_tokens = (
        attributes.get("gen_ai.usage.input_tokens")
        or attributes.get("gen_ai_usage_input_tokens")
        or attributes.get("input_tokens")
    )

    print("input_tokens:", input_tokens)

    if input_tokens is not None:
        total_input_tokens += int(input_tokens)

print("\nTOTAL INPUT TOKENS:", total_input_tokens)
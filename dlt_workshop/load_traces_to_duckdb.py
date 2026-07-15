import os
from pathlib import Path

import dlt
from dotenv import load_dotenv
from logfire.experimental.query_client import LogfireQueryClient


load_dotenv(dotenv_path=Path(".env"), override=True)

read_token = os.getenv("LOGFIRE_READ_TOKEN")
base_url = os.getenv("LOGFIRE_BASE_URL")

client = LogfireQueryClient(
    read_token=read_token,
    base_url=base_url,
)

# Trace with tool calling, 5 spans
trace_id = "019f64dce012f377b9a3be99bbedb647"

sql = f"""
SELECT *
FROM records
WHERE trace_id = '{trace_id}'
ORDER BY start_timestamp
"""

result = client.query_json_rows(sql)
records = result["rows"]

print(f"Loaded {len(records)} records from Logfire")

pipeline = dlt.pipeline(
    pipeline_name="agent_traces_pipeline",
    destination="duckdb",
    dataset_name="agent_traces",
)

load_info = pipeline.run(
    records,
    table_name="records",
)

print(load_info)
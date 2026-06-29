# HBase Implementation

## Purpose

HBase was used to store user session data because session records are high-volume, semi-structured, and time-oriented. In an e-commerce system, user sessions can grow very quickly because every browsing activity, page view, cart action, and conversion event may generate session data.

HBase is suitable for this type of data because it supports distributed storage, sparse columns, and fast row-key-based access.

## Table Name

```text
user_sessions
```

## Column Families

```text
info
device
activity
cart
```

## Column Family Design

| Column Family | Purpose                                                                                          |
| ------------- | ------------------------------------------------------------------------------------------------ |
| `info`        | Stores basic session information such as user ID, session ID, start time, end time, and duration |
| `device`      | Stores device-related information such as device type, operating system, and browser             |
| `activity`    | Stores browsing activity such as viewed products, page views, and conversion status              |
| `cart`        | Stores cart contents for the session                                                             |

## Row Key Design

The row key format used was:

```text
user_id#start_time#session_id
```

Example:

```text
user_000068#2026-04-05T02:38:08#sess_fd011b4e68
```

## Row Key Justification

| Row Key Component | Reason                                                         |
| ----------------- | -------------------------------------------------------------- |
| `user_id`         | Allows efficient retrieval of all sessions for a specific user |
| `start_time`      | Preserves chronological ordering of sessions                   |
| `session_id`      | Ensures row key uniqueness                                     |

This design supports user-level session lookup using prefix scans.

## Table Creation

The HBase table was created using the HBase shell.

```ruby
create 'user_sessions', 'info', 'device', 'activity', 'cart'
```

## Manual Test Insert

A manual test row was inserted first to confirm that the table and column families were working correctly.

```ruby
put 'user_sessions', 'user_000068#2026-04-05T03:31:30#sess_fd011b4e68', 'info:user_id', 'user_000068'
put 'user_sessions', 'user_000068#2026-04-05T03:31:30#sess_fd011b4e68', 'info:session_id', 'sess_fd011b4e68'
put 'user_sessions', 'user_000068#2026-04-05T03:31:30#sess_fd011b4e68', 'info:start_time', '2026-04-05T03:31:30'
put 'user_sessions', 'user_000068#2026-04-05T03:31:30#sess_fd011b4e68', 'activity:conversion_status', 'converted'
```

## Data Loading Method

Session data was loaded using a Python script:

```text
scripts/load_sessions_to_hbase.py
```

The script reads data from:

```text
data/sessions_0.json
```

During development, only the first 100 sessions were loaded into HBase to validate the schema, row-key design, and query pattern.

## Development Load Result

```text
Loaded sessions: 100
Manual test row: 1
Total rows verified: 101
```

## Verification Command

```ruby
count 'user_sessions'
```

Result:

```text
101 row(s)
```

## User Session Query

To retrieve all sessions for a specific user, a prefix scan was used.

```ruby
scan 'user_sessions', {
  FILTER => "PrefixFilter('user_000068')"
}
```

Result:

```text
3 row(s)
```

This confirmed that the row-key strategy works correctly because all rows beginning with `user_000068` were returned.

## Query Interpretation

The query returned multiple sessions for the same user, including session details such as:

```text
info:user_id
info:session_id
info:start_time
info:end_time
info:duration_seconds
device:type
device:os
device:browser
activity:viewed_products
activity:page_views
activity:conversion_status
cart:contents
```

This proves that HBase can store and retrieve semi-structured session activity efficiently.

## Development Limitation

The Python script used HBase shell `put` commands to load session data. This approach is acceptable for development and validation, but it is not ideal for very large-scale production loading.

For full-scale execution, a better approach would be:

```text
Spark-to-HBase integration
HBase bulk loading
MapReduce-based bulk import
```

## Summary

HBase was successfully used to store e-commerce session data. The implementation created a `user_sessions` table with four column families, loaded session records, verified row counts, and demonstrated user-specific session retrieval using prefix-based row-key scanning.

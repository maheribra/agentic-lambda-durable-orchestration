# Project Metrics

## Overview

Measured from real AWS Lambda Durable Functions executions using deployed function version `25`, with additional retry and crash evidence captured from earlier deployed versions.

These metrics are based on execution histories and AWS Lambda durable execution APIs rather than estimated values.

## Workflow Metrics

| Metric | Measured Result | Evidence |
|---|---:|---|
| Durable steps — LOW-risk execution | 9 | `doc001-v25-success-history.json` |
| Durable steps — HIGH-risk execution | 10 | `high-v25-approved-history.json` |
| LOW-risk end-to-end duration | 3.123 seconds | AWS durable execution `DOC-001` |
| HIGH-risk end-to-end duration | 84.696 seconds | AWS durable execution `DOC-HIGH-001` |
| LOW-risk execution result | SUCCEEDED | AWS durable execution |
| HIGH-risk execution result | SUCCEEDED | AWS durable execution |
| Lambda version tested | 25 | AWS Lambda |
| Runtime | Python 3.13 | AWS Lambda |
| Lambda memory | 1024 MB | AWS Lambda |
| Lambda timeout | 900 seconds | AWS Lambda |

## Step-Level Retry Metrics

The retry test used `DOC-RECOVERY-001` and a durable step configured with a maximum of two attempts.

| Metric | Measured Result |
|---|---:|
| Maximum configured attempts | 2 |
| Attempt 1 result | FAILED |
| Retry delay | 1 second |
| Attempt 1 duration | 2.607 seconds |
| Attempt 2 result | SUCCEEDED |
| Attempt 2 duration | 0.278 seconds |
| Total retry-step execution window | 3.807 seconds |
| Final workflow result | SUCCEEDED |

Evidence:

`recovery001-v20-history.json`

The execution history records the first attempt as failed, a one-second retry delay, and the second attempt as successful.

## Runtime Crash / Checkpoint Metrics

A dedicated runtime-crash test was executed against deployed version `24`.

The workflow intentionally terminated during the runtime crash test after the preceding durable operations completed.

| Checkpointed operation | Result |
|---|---|
| `prepare_document` | Completed |
| `analyze_document` | Completed |
| `score_document` | Completed |
| `mcp_enrichment` | Completed |

### Measured Step Durations

| Operation | Duration |
|---|---:|
| `prepare_document` | 2.447 seconds |
| `analyze_document` | 1.071 seconds |
| `score_document` | 1.078 seconds |
| `mcp_enrichment` | 1.098 seconds |

The last recorded completed checkpoint ended at:

`2026-08-17T07:01:31.379000+01:00`

Evidence:

`crash-v24-history.json`

The test proves that completed durable operations were persisted before the injected runtime termination.

## Human-in-the-Loop Metrics

The HIGH-risk execution demonstrated a real durable callback.

| Metric | Result |
|---|---|
| Risk level | HIGH |
| Routing decision | `human-review` |
| Callback created | Yes |
| Callback completed | Yes |
| Workflow resumed after callback | Yes |
| Final execution status | SUCCEEDED |
| Audit record created | Yes |

The HIGH-risk execution took `84.696 seconds` end-to-end. This duration includes the period during which the durable workflow waited for the external human-approval callback.

Evidence:

`high-v25-approved-history.json`

## MCP Enrichment Metrics

The deployed workflow successfully executed the MCP-style enrichment stage.

| Metric | Result |
|---|---|
| MCP-style enrichment executed | Yes |
| LOW-risk enrichment | `MCP-REF-DOC-001` |
| HIGH-risk enrichment | `MCP-REF-DOC-HIGH-001` |
| Enrichment source | `simulated-mcp` |

The enrichment implementation is intentionally deterministic and simulated for portfolio reproducibility; it does not claim to be a production external MCP server integration.

## Audit Metrics

Both measured end-to-end executions produced final audit records.

| Execution | Audit status |
|---|---|
| `DOC-001` | `recorded` |
| `DOC-HIGH-001` | `recorded` |

The audit data includes routing, approval, processing, and recovery results.

## Evidence Files

The repository contains execution-history evidence for the measured scenarios:

- `doc001-v25-success-history.json` — LOW-risk successful end-to-end execution
- `high-v25-approved-history.json` — HIGH-risk routing, human approval, processing, recovery, and audit completion
- `recovery001-v20-history.json` — durable step-level retry
- `crash-v24-history.json` — runtime crash and checkpoint persistence

## Limitations

These metrics deliberately distinguish between mechanisms that were demonstrated and mechanisms that were not.

### Proven

- Durable multi-step execution
- Durable step checkpointing
- Step-level retry
- Human-in-the-loop callback and workflow resumption
- Deterministic LOW/HIGH routing
- MCP-style enrichment
- Audit record generation
- Runtime crash checkpoint persistence

### Not Claimed

Automatic replay of an already `FAILED` whole durable execution has **not** been claimed.

The crash test demonstrated that completed durable operations were persisted before runtime termination. It did not demonstrate automatic resumption of the same already-failed execution through the remaining workflow steps.

This distinction keeps the project's claims aligned with the captured AWS execution evidence.

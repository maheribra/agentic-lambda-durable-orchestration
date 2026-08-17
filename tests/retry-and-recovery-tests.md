# Retry and Recovery Tests

## 1. Step-Level Retry Test

### Objective

Verify that a transient failure inside a durable step is automatically retried without restarting the entire workflow.

### Test Input

```json
{
  "document_id": "DOC-RECOVERY-001"
}
```

### Result

**PASS** — The simulated transient failure was recovered through durable step-level retry.

## 2. Human-in-the-Loop Callback Test

**PASS** — A HIGH-risk document entered human review, the callback was completed, and the workflow resumed to completion.

## 3. HIGH-Risk Conditional Routing Test

**PASS** — HIGH-risk documents were routed to human review while LOW-risk documents followed standard processing.

## 4. Workflow-Level Runtime Crash / Checkpoint Persistence Test

### Objective

Verify that completed durable steps remain checkpointed when the Lambda runtime terminates during execution.

### Test Input

```json
{
  "document_id": "DOC-CRASH-001"
}
```

### Failure Injection

The workflow intentionally terminates the Lambda runtime immediately after MCP enrichment.

### Result

Execution history showed successful completion of:

- prepare_document
- analyze_document
- score_document
- mcp_enrichment

The execution then failed before route_document completed.

**PASS — Checkpoint Persistence**

Completed durable steps were recorded before the runtime failure.

**NOT PROVEN — Automatic Execution Replay**

This test does not claim that the failed execution automatically resumed. Step-level retry and execution-level crash recovery are separate mechanisms.

## 5. Overall Test Results

| Test | Result |
|---|---|
| Step-level transient retry | PASS |
| Human approval callback | PASS |
| HIGH-risk conditional routing | PASS |
| MCP enrichment | PASS |
| Audit record creation | PASS |
| Runtime crash checkpoint persistence | PASS |
| Automatic whole-execution crash replay | NOT CLAIMED |

## Evidence

Execution histories were captured using AWS Lambda durable execution history APIs.

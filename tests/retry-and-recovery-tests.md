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

The durable step was configured with a retry strategy allowing two attempts. The first attempt intentionally failed and the subsequent attempt completed successfully.

---

## 2. Human-in-the-Loop Callback Test

**PASS** — A HIGH-risk document entered human review, the callback was completed, and the workflow resumed to completion.

---

## 3. HIGH-Risk Conditional Routing Test

**PASS** — HIGH-risk documents were routed to human review while LOW-risk documents followed standard processing.

---

## 4. MCP Enrichment Test

**PASS** — The workflow successfully invoked the MCP enrichment tool binding and incorporated the enrichment result into the durable workflow.

---

## 5. Audit Record Test

**PASS** — The workflow created a final audit record containing routing, approval, processing, and recovery results.

---

## 6. Workflow-Level Runtime Crash / Checkpoint Persistence Test

### Objective

Verify that completed durable steps remain checkpointed when the Lambda runtime terminates during execution.

### Test Input

```json
{
  "document_id": "DOC-CRASH-001"
}
```

### Failure Injection

The workflow intentionally terminates the Lambda runtime during the dedicated `simulated_runtime_crash` durable step after the preceding durable steps have completed.

### Result

Execution history showed successful completion of:

* `prepare_document`
* `analyze_document`
* `score_document`
* `mcp_enrichment`

The runtime then exited with:

```text
Runtime.ExitError
```

The durable execution was marked:

```text
FAILED
```

**PASS — Checkpoint Persistence**

The execution history demonstrates that the durable steps completed before the runtime failure were persisted.

### Important Limitation

**NOT CLAIMED — Automatic Whole-Execution Crash Replay**

This test does not claim that the same failed execution automatically resumed after the Lambda runtime terminated.

Step-level retry and whole-execution runtime recovery are separate mechanisms. The available AWS Lambda durable execution APIs used in this project do not expose a resume/restart operation for an already `FAILED` durable execution.

Therefore:

* **Step-level retry:** proven.
* **Checkpoint persistence across runtime termination:** proven.
* **Automatic replay of the entire failed execution:** not claimed.

This distinction prevents conflating durable step retry with whole-execution runtime recovery.

### Evidence

Evidence captured from execution version 24:

```text
crash-v24-history.json
```

The history contains successful operations for:

```text
prepare_document
analyze_document
score_document
mcp_enrichment
```

before the injected runtime termination.

---

## 7. Overall Test Results

| Test                                   | Result      |
| -------------------------------------- | ----------- |
| Step-level transient retry             | PASS        |
| Human approval callback                | PASS        |
| HIGH-risk conditional routing          | PASS        |
| MCP enrichment                         | PASS        |
| Audit record creation                  | PASS        |
| Runtime crash checkpoint persistence   | PASS        |
| Automatic whole-execution crash replay | NOT CLAIMED |

## Evidence

Execution histories were captured using AWS Lambda durable execution history APIs.

The primary runtime crash evidence is:

```text
crash-v24-history.json
```

The project also includes execution histories for retry, HITL callback, routing, enrichment, processing, and audit scenarios.

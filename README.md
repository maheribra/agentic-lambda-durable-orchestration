# Orchestrating Agentic Applications with AWS Lambda Durable Functions

A portfolio project demonstrating AWS Lambda Durable Functions for orchestrating a multi-step, stateful document-review workflow with durable checkpoints, deterministic routing, retries, MCP-style enrichment, human-in-the-loop approval, and auditability.

## Architecture

```text
Document
    |
    v
Prepare Document
    |
    v
AI-Style Analysis
    |
    v
Risk / Quality Scoring
    |
    v
MCP Enrichment
    |
    v
Conditional Routing
    |
    +---- LOW ----> Standard Processing
    |
    +---- HIGH ---> Human Approval
                         |
                         v
                    Callback / Wait
                         |
                         v
                   Process Approved
                         |
                         v
                    Recovery Step
                         |
                         v
                     Audit Record
                         |
                         v
                      Complete
```

## What This Project Demonstrates

* AWS Lambda Durable Functions
* Durable step checkpointing
* Replay-aware orchestration
* Deterministic workflow routing
* Step-level retry and recovery
* Human-in-the-loop callbacks
* Long-running workflow suspension and resumption
* MCP-style external enrichment
* Risk-based conditional routing
* Audit record generation
* Durable execution history
* Runtime failure and checkpoint-persistence testing
* Infrastructure deployment with AWS SAM

## Durable Execution

Each important workflow operation is implemented as a durable operation rather than relying on ordinary in-memory Lambda execution.

Completed operations are checkpointed by the Durable Execution runtime.

The workflow execution history can be inspected through AWS Lambda Durable Execution APIs.

## Recovery Testing

The project demonstrates two distinct recovery concepts.

### Step-Level Retry

A transient failure is deliberately injected into a durable step.

The Durable Execution SDK retries the step according to its retry configuration and the workflow continues after the step succeeds.

### Runtime Crash and Checkpoint Persistence

A separate test intentionally terminates the Lambda runtime after these operations have completed:

* `prepare_document`
* `analyze_document`
* `score_document`
* `mcp_enrichment`

The resulting execution history confirms that these completed operations were persisted before the runtime failure.

The project intentionally does **not** claim that this test proves automatic whole-execution crash replay.

Step-level retry and execution-level failure/recovery are separate mechanisms.

See [`tests/retry-and-recovery-tests.md`](tests/retry-and-recovery-tests.md).

## Human-in-the-Loop

HIGH-risk documents are routed to human review.

The workflow creates a durable callback and waits for an external approval decision.

Once the callback succeeds, the workflow resumes and continues processing without losing the previous workflow state.

## Conditional Routing

The workflow uses deterministic risk scoring.

* **LOW risk** -> `standard-processing`
* **HIGH risk** -> `human-review`

This makes the routing behavior reproducible and suitable for demonstrating durable orchestration concepts.

## MCP-Style Enrichment

The workflow includes an MCP-style enrichment stage between risk scoring and routing.

For portfolio reproducibility, the enrichment and AI-style analysis components use deterministic simulated responses rather than requiring a live external LLM or MCP server.

This is intentional.

The simulated components can later be replaced with:

* Amazon Bedrock
* A real MCP server
* External APIs
* Enterprise knowledge systems
* Other agentic tools

The project therefore demonstrates the orchestration architecture without introducing unnecessary external dependencies or nondeterministic behavior.

## Why Durable Functions?

A conventional workflow implementation may require the application to manage:

* execution state
* retries
* checkpoints
* callback state
* failure recovery
* long waits
* idempotency
* resumption

AWS Lambda Durable Functions provides runtime support for durable execution state and workflow progress.

This project explores that model using a realistic document-review workflow.

## Durable Functions vs Traditional Automation

Tools such as n8n are excellent for visual automation and integrations.

Durable Functions targets a different problem: programmatic orchestration where application code controls workflow behavior while the runtime provides durable execution semantics.

This project focuses on:

* code-first orchestration
* durable state
* deterministic replay
* checkpointed execution
* programmatic branching
* retries
* callbacks
* AWS-native execution

The goal is not to claim that one approach universally replaces the other, but to demonstrate when code-first durable orchestration is useful.

## Technology Stack

* Python 3.13
* AWS Lambda Durable Functions
* `aws-durable-execution-sdk-python`
* AWS SAM
* AWS CloudFormation
* Amazon CloudWatch
* AWS CLI
* Git / GitHub

## Project Structure

```text
agentic-lambda-durable-orchestration/
|
+-- workflows/
|   +-- multi_step_reasoning.py
|
+-- steps/
|   +-- workflow step implementations
|
+-- tests/
|   +-- retry-and-recovery-tests.md
|
+-- template.yaml
+-- requirements.txt
+-- .gitignore
+-- README.md
```

## Deployment

The application is deployed with AWS SAM.

### Build

```bash
sam build
```

### Validate

```bash
sam validate
```

### Deploy

```bash
sam deploy
```

## Testing

The project includes execution-history-based testing for durable workflow behavior.

Tests cover:

* successful multi-step execution
* deterministic LOW/HIGH routing
* human approval callbacks
* step-level retry behavior
* MCP-style enrichment
* audit record generation
* runtime crash and checkpoint persistence
* durable execution history inspection

The final deployed workflow was verified on AWS Lambda function version `25`.

Evidence includes:

* `doc001-v25-success-history.json` — successful LOW-risk end-to-end execution
* `high-v25-approved-history.json` — HIGH-risk routing, human approval callback, processing, recovery, and audit completion
* `crash-v24-history.json` — runtime crash and checkpoint persistence evidence

Execution histories are inspected using AWS Lambda Durable Execution APIs.

The project deliberately distinguishes between step-level retry and whole-execution runtime recovery. Automatic replay of an already failed execution is not claimed because it was not demonstrated by the available test evidence.

### Automated Unit Tests

The repository also includes automated unit tests for deterministic workflow logic.

Run:

    python -m pytest -q

Current result:

* **6 tests passed**
* **0 tests failed**

The tests cover:

* LOW/HIGH risk classification
* deterministic routing
* approved-document processing
* audit-record generation

Test implementation:

`tests/test_workflow_logic.py`

## Engineering Focus

This project is designed to demonstrate practical AWS serverless engineering through a realistic agentic document-review workflow.

Key engineering themes include:

* durable execution
* fault tolerance
* checkpointing
* deterministic orchestration
* human approval workflows
* recovery testing
* AWS-native architecture
* infrastructure as code
* observable execution history

## Project Status

The core durable orchestration workflow has been deployed and tested on AWS.

Verified capabilities include:

* multi-step durable execution
* document preparation
* AI-style analysis
* risk scoring
* MCP-style enrichment
* deterministic routing
* HIGH-risk human approval
* callback-based workflow resumption
* audit recording
* step-level recovery testing
* runtime crash and checkpoint-persistence testing
* AWS SAM deployment

The project deliberately distinguishes between **step-level retry** and **execution-level runtime failure/recovery**, avoiding claims that are not demonstrated by the test evidence.

from aws_durable_execution_sdk_python import (
    DurableContext,
    durable_execution,
    durable_step,
)

from aws_durable_execution_sdk_python.config import (
    Duration,
    WaitForCallbackConfig,
    StepConfig,
)

from aws_durable_execution_sdk_python.serdes import DEFAULT_JSON_SERDES

from aws_durable_execution_sdk_python.retries import (
    RetryStrategyConfig,
    JitterStrategy,
    create_retry_strategy,
)

from tools.mcp_tool_bindings import enrich_document


@durable_step
def prepare_document(
    context: DurableContext,
    document_id: str,
) -> dict:
    return {
        "document_id": document_id,
        "status": "prepared",
        "content": f"Prepared document {document_id}",
    }


@durable_step
def analyze_document(
    context: DurableContext,
    prepared_document: dict,
) -> dict:
    document_id = prepared_document["document_id"]

    if document_id.startswith("DOC-HIGH"):
        quality_score = 0.65
        issues_found = 4
        summary = "High-risk document requiring human review"
    else:
        quality_score = 0.85
        issues_found = 1
        summary = "Document analyzed successfully"

    return {
        "document_id": document_id,
        "summary": summary,
        "quality_score": quality_score,
        "issues_found": issues_found,
    }


@durable_step
def score_document(
    context: DurableContext,
    analysis: dict,
) -> dict:
    quality_score = analysis["quality_score"]

    if quality_score >= 0.8:
        risk_level = "LOW"
    else:
        risk_level = "HIGH"

    return {
        "document_id": analysis["document_id"],
        "risk_level": risk_level,
        "score": quality_score,
    }


@durable_step
def mcp_enrichment(
    context: DurableContext,
    document_id: str,
    risk_level: str,
) -> dict:
    return enrich_document(document_id, risk_level)


@durable_step
def route_document(
    context: DurableContext,
    risk_level: str,
) -> dict:
    if risk_level == "HIGH":
        route = "human-review"
    else:
        route = "standard-processing"

    return {
        "risk_level": risk_level,
        "route": route,
    }


def submit_for_human_approval(
    callback_id: str,
    callback_context,
) -> None:
    print(
        f"HITL APPROVAL REQUIRED | callback_id={callback_id}"
    )


def human_approval(
    context: DurableContext,
    routing: dict,
) -> dict:
    if routing["route"] != "human-review":
        return {
            "required": False,
            "status": "not-required",
        }

    approval_result = context.wait_for_callback(
        submit_for_human_approval,
        name="human_approval",
        config=WaitForCallbackConfig(
            timeout=Duration.from_hours(1),
            serdes=DEFAULT_JSON_SERDES,
        ),
    )

    return {
        "required": True,
        "status": "approved",
        "decision": approval_result,
    }


@durable_step
def process_approved_document(
    context: DurableContext,
    document_id: str,
    approval: dict,
) -> dict:
    return {
        "document_id": document_id,
        "action": "standard-processing",
        "approval": approval,
        "status": "processed",
    }


@durable_step
def simulated_recovery_step(
    context: DurableContext,
    document_id: str,
) -> dict:
    # Durable SDK exposes the current step attempt through
    # the logger metadata created by StepOperationExecutor.
    attempt = context.logger._default_extra.get("attempt", 1)

    # Deliberately fail only on the first attempt.
    # The configured retry strategy should replay this step,
    # after which attempt 2 succeeds.
    if document_id == "DOC-RECOVERY-001" and attempt == 1:
        raise RuntimeError("SIMULATED_TRANSIENT_FAILURE")

    return {
        "status": "recovered",
        "document_id": document_id,
        "attempt": attempt,
    }


@durable_step
def create_audit_record(
    context: DurableContext,
    document_id: str,
    routing: dict,
    approval: dict,
    processing: dict,
    recovery: dict,
) -> dict:
    return {
        "document_id": document_id,
        "routing": routing,
        "approval": approval,
        "processing": processing,
        "recovery": recovery,
        "audit_status": "recorded",
    }


recovery_retry_strategy = create_retry_strategy(
    RetryStrategyConfig(
        max_attempts=2,
        initial_delay=Duration.from_seconds(1),
        max_delay=Duration.from_seconds(1),
        backoff_rate=1,
        jitter_strategy=JitterStrategy.NONE,
    )
)


@durable_execution
def handler(
    event,
    context: DurableContext,
):
    document_id = event.get(
        "document_id",
        "DOC-001",
    )

    prepared_document = context.step(
        prepare_document(document_id),
        name="prepare_document",
    )

    analysis = context.step(
        analyze_document(prepared_document),
        name="analyze_document",
    )

    scoring = context.step(
        score_document(analysis),
        name="score_document",
    )

    enrichment = context.step(
        mcp_enrichment(
            document_id,
            scoring["risk_level"],
        ),
        name="mcp_enrichment",
    )

    routing = context.step(
        route_document(
            scoring["risk_level"],
        ),
        name="route_document",
    )

    approval = human_approval(
        context,
        routing,
    )

    processing = context.step(
        process_approved_document(
            document_id,
            approval,
        ),
        name="process_approved_document",
    )

    recovery = context.step(
        simulated_recovery_step(document_id),
        name="simulated_recovery_step",
        config=StepConfig(
            retry_strategy=recovery_retry_strategy,
        ),
    )

    audit = context.step(
        create_audit_record(
            document_id,
            routing,
            approval,
            processing,
            recovery,
        ),
        name="audit_record",
    )

    return {
        "status": "complete",
        "document_id": document_id,
        "prepared": prepared_document,
        "analysis": analysis,
        "scoring": scoring,
        "enrichment": enrichment,
        "routing": routing,
        "approval": approval,
        "processing": processing,
        "recovery": recovery,
        "audit": audit,
    }
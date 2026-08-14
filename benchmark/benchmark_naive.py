def prepare_document(document_id):
    return {
        "document_id": document_id,
        "status": "prepared",
    }


def analyze_document(prepared):
    return {
        "document_id": prepared["document_id"],
        "quality_score": 0.85,
    }


def score_document(analysis):
    return {
        "document_id": analysis["document_id"],
        "risk_level": "LOW" if analysis["quality_score"] >= 0.8 else "HIGH",
    }


def mcp_enrichment(document_id, risk_level):
    return {
        "document_id": document_id,
        "risk_level": risk_level,
        "source": "simulated-mcp",
    }


def route_document(risk_level):
    return "standard-processing" if risk_level == "LOW" else "human-review"


def process_document(document_id, route):
    return {
        "document_id": document_id,
        "route": route,
        "status": "processed",
    }


def simulate_failure():
    raise RuntimeError("SIMULATED_FAILURE_AFTER_MCP")


def main():
    document_id = "DOC-BENCHMARK-FAILURE-001"

    try:
        prepared = prepare_document(document_id)
        analysis = analyze_document(prepared)
        scoring = score_document(analysis)
        enrichment = mcp_enrichment(
            document_id,
            scoring["risk_level"],
        )

        simulate_failure()

        route = route_document(scoring["risk_level"])
        result = process_document(document_id, route)

        print(result)

    except RuntimeError as error:
        print("Naive orchestration failed:")
        print(error)
        print("Recovery behavior: entire workflow must be restarted.")


if __name__ == "__main__":
    main()
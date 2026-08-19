from workflows.multi_step_reasoning import (
    analyze_prepared_document,
    calculate_risk,
    determine_route,
)


def test_analyze_low_document():
    prepared = {
        "document_id": "DOC-001",
        "status": "prepared",
    }

    result = analyze_prepared_document(prepared)

    assert result["quality_score"] == 0.85
    assert result["issues_found"] == 1


def test_analyze_high_document():
    prepared = {
        "document_id": "DOC-HIGH-001",
        "status": "prepared",
    }

    result = analyze_prepared_document(prepared)

    assert result["quality_score"] == 0.65
    assert result["issues_found"] == 4


def test_score_document_low():
    analysis = {
        "document_id": "DOC-001",
        "quality_score": 0.9,
    }

    result = calculate_risk(analysis)

    assert result["risk_level"] == "LOW"


def test_score_document_high():
    analysis = {
        "document_id": "DOC-HIGH-001",
        "quality_score": 0.65,
    }

    result = calculate_risk(analysis)

    assert result["risk_level"] == "HIGH"


def test_route_document_low():
    result = determine_route("LOW")

    assert result["route"] == "standard-processing"


def test_route_document_high():
    result = determine_route("HIGH")

    assert result["route"] == "human-review"
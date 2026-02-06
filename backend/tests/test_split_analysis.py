import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from models.user import User
from models.analysis import Analysis
from core.security import create_access_token

from models import get_db

@pytest.fixture
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def mock_llm_engine():
    with patch("pipeline.llm_engine.LLMEngine.optimize") as mock:
        yield mock

def test_analyze_rules_only(client, test_db, test_user):
    # Test anonymous
    response = client.post(
        "/api/v1/analyze/rules-only",
        json={"text": "She go to school.", "mode": "accuracy"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["original_text"] == "She go to school."
    assert data["data"]["status"] == "rule_only"
    assert len(data["data"]["errors"]) > 0
    
    # Verify DB
    analysis = test_db.query(Analysis).filter(Analysis.id == data["data"]["analysis_id"]).first()
    assert analysis is not None
    assert analysis.status == "rule_only"
    assert analysis.user_id is None # Anonymous

def test_optimize_llm_auth_required(client):
    response = client.post(
        "/api/v1/analyze/optimize-llm",
        json={"analysis_id": "123e4567-e89b-12d3-a456-426614174000"}
    )
    assert response.status_code == 401

def test_optimize_llm_flow(client, test_db, test_user, mock_llm_engine):
    # 1. Create analysis via rules-only (logged in)
    token = create_access_token(data={"sub": str(test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/api/v1/analyze/rules-only",
        json={"text": "She go to school.", "mode": "accuracy"},
        headers=headers
    )
    assert response.status_code == 200
    analysis_id = response.json()["data"]["analysis_id"]
    
    # Mock LLM response
    mock_result = MagicMock()
    mock_result.optimized_text = "She goes to school."
    mock_result.token_usage = {"total_tokens": 10}
    mock_result.metadata = {
        "learning_analysis": {
            "error_patterns": [],
            "ea_learning_recommendations": [],
            "personalized_tips": []
        }
    }
    mock_llm_engine.return_value = mock_result

    # 2. Optimize
    response = client.post(
        "/api/v1/analyze/optimize-llm",
        json={"analysis_id": analysis_id},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "llm_completed"
    assert data["data"]["corrected_text"] == "She goes to school."
    assert "learning_analysis" in data["data"]["statistics"]
    
    # 3. Verify DB
    test_db.expire_all()
    analysis = test_db.query(Analysis).filter(Analysis.id == analysis_id).first()
    assert analysis.status == "llm_completed"
    assert analysis.corrected_text == "She goes to school."

def test_optimize_llm_idempotency(client, test_db, test_user, mock_llm_engine):
    # Setup completed analysis
    token = create_access_token(data={"sub": str(test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    
    # Manually create analysis
    analysis = Analysis(
        user_id=test_user.id,
        original_text="test",
        corrected_text="test",
        mode="accuracy",
        status="llm_completed"
    )
    test_db.add(analysis)
    test_db.commit()
    
    response = client.post(
        "/api/v1/analyze/optimize-llm",
        json={"analysis_id": str(analysis.id)},
        headers=headers
    )
    assert response.status_code == 409

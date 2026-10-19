def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "models" in data

def test_scan_email_safe(client):
    payload = {
        "subject": "Lunch today?",
        "sender": "colleague@company.com",
        "receiver": "me@company.com",
        "body": "Hey, are we still on for lunch at 12:30?"
    }

    response = client.post("/api/v1/scan", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"

    result = data["data"]
    assert "id" in result
    assert result["classification"] in ["safe", "suspicious", "phishing"]
    assert 0 <= result["risk_score"] <= 100
    assert "explanation" in result
    assert "indicators" in result

def test_scan_email_validation_error(client):
    payload = {
        "subject": "Missing fields"
        # sender and body are missing
    }

    response = client.post("/api/v1/scan", json=payload)
    assert response.status_code == 422  # Validation error

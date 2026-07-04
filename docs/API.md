# API Documentation

The PhishGuard AI API is structured around REST principles. All requests and responses use JSON format.

## Authentication

Authentication is performed using JWT (JSON Web Tokens) or API Keys.

### JWT Bearer Authentication
To access protected endpoints, provide the token in the `Authorization` header:
```http
Authorization: Bearer <your_jwt_token>
```

### API Key Authentication
Provide your generated developer API key in the custom header:
```http
X-API-Key: <your_api_key>
```

---

## Endpoint Reference

### 1. Authentication

#### `POST /api/v1/auth/register`
Creates a new user account.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword123",
    "full_name": "John Doe"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "id": "usr_9b1deb4d3b7d4fcfb1d4...",
      "email": "user@example.com",
      "username": "johndoe",
      "full_name": "John Doe",
      "role": "user",
      "created_at": "2026-07-04T12:00:00Z"
    }
  }
  ```

#### `POST /api/v1/auth/login`
Authenticates a user and issues a JWT token.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
      "token_type": "bearer",
      "expires_in": 14400,
      "user": {
        "id": "usr_9b...",
        "email": "user@example.com",
        "username": "johndoe"
      }
    }
  }
  ```

---

### 2. Email Scanning

#### `POST /api/v1/scan`
Submits an email for threat analysis.
- **Request Body**:
  ```json
  {
    "subject": "Urgent: Verify your banking details",
    "sender": "security@chase-banking-security.com",
    "receiver": "victim@example.com",
    "body": "Your bank account has been locked. Verify immediately: http://chase-banking-security.com/login"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "id": "scn_5a21...",
      "classification": "phishing",
      "confidence": 0.942,
      "risk_score": 85.5,
      "probabilities": {
        "safe": 0.012,
        "suspicious": 0.046,
        "phishing": 0.942
      },
      "explanation": "This email displays critical phishing indicators, including brand impersonation (Chase) and suspicious links.",
      "security_report": {
        "executive_summary": "High risk of credential harvesting...",
        "recommended_actions": [
          "Do not click the links provided.",
          "Flag the email as spam."
        ],
        "security_score": 14
      }
    }
  }
  ```

---

### 3. History & Exports

#### `GET /api/v1/history`
Retrieves past scan entries. Supports pagination, full-text search, and classification filters.
- **Query Parameters**:
  - `page`: Page index (default: `1`)
  - `page_size`: Results per page (default: `20`)
  - `classification`: Filter by classification type (`safe`, `suspicious`, `phishing`)
  - `search`: Full text keyword filter
- **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "items": [
        {
          "id": "scn_5a21...",
          "subject": "Urgent: Verify your banking details",
          "sender": "security@chase-banking-security.com",
          "classification": "phishing",
          "risk_score": 85.5,
          "is_favorite": false,
          "created_at": "2026-07-04T12:05:00Z"
        }
      ],
      "total": 1,
      "page": 1,
      "page_size": 20,
      "total_pages": 1
    }
  }
  ```

#### `GET /api/v1/history/export`
Exports scan history.
- **Query Parameters**:
  - `format`: Format of download file (`csv` or `json`, default: `csv`)
- **Response (200 OK)**: Plain text CSV file or JSON array matching request disposition.

---

### 4. Dashboard Metrics

#### `GET /api/v1/dashboard/statistics`
Returns aggregations of scan counts and safety indicators.
- **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "total_scans": 230,
      "safe_count": 140,
      "suspicious_count": 35,
      "phishing_count": 55,
      "average_risk_score": 38.4,
      "daily_scans": 12,
      "weekly_scans": 84
    }
  }
  ```

#### `GET /api/v1/dashboard/trends`
Aggregates daily scans for historical timeline charting.
- **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": [
      {
        "date": "2026-07-01",
        "safe": 12,
        "suspicious": 2,
        "phishing": 4,
        "total": 18
      }
    ]
  }
  ```

---

### 6. Models & Metrics

#### `GET /api/v1/models/status`
Returns operational status of each AI engine.

#### `GET /api/v1/models/metrics`
Returns persisted evaluation metrics (F1 scores, holdout method, ensemble weights).

#### `GET /api/v1/models/info`
Returns model status, ML metrics, hybrid architecture, runtime performance, and explainability metadata.

#### `GET /api/v1/metrics`
Returns scan statistics, feedback accuracy, and live latency samples.

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import patch, MagicMock
from app import app

app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'test-secret-key'
app.config['WTF_CSRF_ENABLED'] = False


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


# ── /register ────────────────────────────────────────────────────────────────

@patch("auth.InventoryModel")
def test_register_get(mock_model_class, client):
    """GET /register renders the registration form"""
    response = client.get("/register")
    assert response.status_code == 200


@patch("auth.InventoryModel")
def test_register_existing_user(mock_model_class, client):
    """Registering with a taken username flashes an error and redirects back"""
    mock_model = MagicMock()
    mock_model.get_user_by_username.return_value = {"id": 1, "username": "taken"}
    mock_model_class.return_value = mock_model

    response = client.post("/register", data={
        "username": "taken",
        "password": "password123"
    })

    assert response.status_code == 302
    assert "/register" in response.headers["Location"]
    mock_model.close.assert_called_once()


@patch("auth.InventoryModel")
def test_register_new_user(mock_model_class, client):
    """Registering with a fresh username creates the user and redirects to login"""
    mock_model = MagicMock()
    mock_model.get_user_by_username.return_value = None  # username is free
    mock_model_class.return_value = mock_model

    response = client.post("/register", data={
        "username": "newuser",
        "password": "password123"
    })

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
    mock_model.create_user.assert_called_once()
    mock_model.close.assert_called_once()


# ── /login ────────────────────────────────────────────────────────────────────

@patch("auth.InventoryModel")
def test_login_get(mock_model_class, client):
    """GET /login renders the login form"""
    response = client.get("/login")
    assert response.status_code == 200


@patch("auth.InventoryModel")
def test_login_invalid_credentials(mock_model_class, client):
    """Wrong password stays on login page"""
    mock_model = MagicMock()
    mock_model.get_user_by_username.return_value = {"id": 1}

    mock_user = MagicMock()
    mock_user.password_hash = "not-a-real-hash"
    mock_model.build_user_object.return_value = mock_user
    mock_model_class.return_value = mock_model

    response = client.post("/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })

    # Stays on login (no redirect)
    assert response.status_code == 200


@patch("auth.InventoryModel")
def test_login_valid_credentials(mock_model_class, client):
    """Correct credentials redirect to inventory"""
    from werkzeug.security import generate_password_hash

    mock_model = MagicMock()
    mock_model.get_user_by_username.return_value = {"id": 1}

    mock_user = MagicMock()
    mock_user.password_hash = generate_password_hash("correctpassword")
    mock_user.is_authenticated = True
    mock_user.is_active = True
    mock_user.is_anonymous = False
    mock_user.get_id.return_value = "1"
    mock_model.build_user_object.return_value = mock_user
    mock_model_class.return_value = mock_model

    response = client.post("/login", data={
        "username": "testuser",
        "password": "correctpassword"
    })

    assert response.status_code == 302
    assert "/" in response.headers["Location"]  # redirects to inventory.index


@patch("auth.InventoryModel")
def test_login_no_user_found(mock_model_class, client):
    """Username not found stays on login page"""
    mock_model = MagicMock()
    mock_model.get_user_by_username.return_value = None
    mock_model.build_user_object.return_value = None
    mock_model_class.return_value = mock_model

    response = client.post("/login", data={
        "username": "ghost",
        "password": "whatever"
    })

    assert response.status_code == 200


# ── /logout ───────────────────────────────────────────────────────────────────

def test_logout_requires_login(client):
    """Unauthenticated request to /logout redirects to login"""
    response = client.get("/logout")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


@patch("auth.InventoryModel")
def test_logout_authenticated(mock_model_class, client):
    """Logged-in user is redirected to login after logout"""
    from werkzeug.security import generate_password_hash

    mock_model = MagicMock()
    mock_model.get_user_by_username.return_value = {"id": 1}

    mock_user = MagicMock()
    mock_user.password_hash = generate_password_hash("pass")
    mock_user.is_authenticated = True
    mock_user.is_active = True
    mock_user.is_anonymous = False
    mock_user.get_id.return_value = "1"
    mock_model.build_user_object.return_value = mock_user
    mock_model_class.return_value = mock_model

    # Log in first
    client.post("/login", data={"username": "testuser", "password": "pass"})

    response = client.get("/logout")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
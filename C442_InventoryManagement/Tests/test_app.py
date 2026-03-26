
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from unittest.mock import patch, MagicMock
from app import app, load_user

# Configure Flask testing mode
app.config['TESTING'] = True
app.config['SECRET_KEY'] = "test-secret-key"


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_home_redirects_to_login(client):
    """
    If we try to access a protected route without login, it should redirect to login
    """
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


@patch("app.InventoryModel")
def test_load_user(mock_model_class):
    """
    Test the load_user function with a mocked InventoryModel
    """
    mock_model = MagicMock()
    mock_model.get_user_by_id.return_value = {"id": 1, "username": "testuser"}
    mock_model.build_user_object.return_value = "user-object"
    mock_model_class.return_value = mock_model

    user = load_user(1)

    mock_model.get_user_by_id.assert_called_once_with(1)
    mock_model.build_user_object.assert_called_once()
    mock_model.close.assert_called_once()
    assert user == "user-object"


@patch("app.InventoryModel")
def test_register_blueprints(mock_model_class):
    """
    Ensure blueprints are registered properly
    """
    assert "auth" in app.blueprints
    assert "inventory" in app.blueprints
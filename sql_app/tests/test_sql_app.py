from unittest import mock
from unittest.mock import patch

from ..main import create_task, login_task


@mock.patch("sql_app.main.crud.get_user_by_email")
@mock.patch("sql_app.main.crud.create_user")
def test_create_task(mock_create_user, mock_get_user_by_email):
    mock_get_user_by_email.return_value = None
    mock_user_dict = {"email": "test@example.com", "password": "password"}
    mock_db_url = "sqlite:///test.db"

    expected_output = {"id": 1, "email": "test@example.com", "password": "password"}
    mock_create_user.return_value.__dict__ = expected_output

    output = create_task(mock_user_dict, mock_db_url)
    assert output == expected_output
    mock_create_user.assert_called_once()
    mock_get_user_by_email.assert_called_once()


def test_login_task():
    email = "test@example.com"
    password = "password"
    db_url = "sqlite:///test.db"

    # Mock the validate_credentials function to return a user
    with patch("sql_app.main.crud.validate_credentials") as mock_validate_credentials:
        mock_validate_credentials.return_value = {"id": 1, "email": email}

        # Call the login_task function
        result = login_task(email, password, db_url)

        # Assert that the result is as expected
        assert result == {"Details": "User logged in successfully"}

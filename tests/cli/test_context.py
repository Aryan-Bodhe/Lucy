from unittest.mock import patch

from lucy.cli.context import request_id_var, session_id_var, session_manager, token_manager


def test_token_manager_sets_and_resets_request_id():
    assert request_id_var.get() == "-"

    with patch("lucy.cli.context.uuid4", return_value="12345678-aaaa-bbbb-cccc-dddddddddddd"):
        with token_manager():
            assert request_id_var.get() == "12345678"

    assert request_id_var.get() == "-"


def test_session_manager_sets_and_resets_session_id():
    assert session_id_var.get() == "-"

    with patch("lucy.cli.context.uuid4", return_value="87654321-aaaa-bbbb-cccc-dddddddddddd"):
        with session_manager():
            assert session_id_var.get() == "87654321"

    assert session_id_var.get() == "-"


def test_nested_contexts_restore_previous_values():
    request_token = request_id_var.set("outer-request")
    session_token = session_id_var.set("outer-session")

    try:
        with patch("lucy.cli.context.uuid4", side_effect=["11111111-aaaa-bbbb-cccc-dddddddddddd", "22222222-aaaa-bbbb-cccc-dddddddddddd"]):
            with token_manager():
                assert request_id_var.get() == "11111111"
                with session_manager():
                    assert session_id_var.get() == "22222222"
                assert session_id_var.get() == "outer-session"
            assert request_id_var.get() == "outer-request"
    finally:
        request_id_var.reset(request_token)
        session_id_var.reset(session_token)

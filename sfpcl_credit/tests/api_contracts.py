"""Test-only assertions for SFPCL API response contracts."""


STANDARD_META_FIELDS = ("request_id", "timestamp", "api_version")
PAGINATION_FIELDS = (
    "page",
    "page_size",
    "total_count",
    "total_pages",
    "has_next",
    "has_previous",
)
ERROR_FIELDS = ("code", "message", "details", "field_errors")
AVAILABLE_ACTION_FIELDS = (
    "action_code",
    "label",
    "enabled",
    "disabled_reason",
    "required_permission",
)


def _assert_field(test_case, payload, field_path):
    current = payload
    traversed = []
    for part in field_path.split("."):
        traversed.append(part)
        test_case.assertIsInstance(
            current,
            dict,
            f"Contract field {'.'.join(traversed[:-1])} must be an object.",
        )
        test_case.assertIn(
            part,
            current,
            f"Missing contract field: {'.'.join(traversed)}",
        )
        current = current[part]
    return current


def assert_standard_meta(test_case, payload):
    meta = _assert_field(test_case, payload, "meta")
    for field in STANDARD_META_FIELDS:
        _assert_field(test_case, payload, f"meta.{field}")
    test_case.assertEqual(meta["api_version"], "v1")


def assert_success_envelope(test_case, payload):
    """Assert the standard success envelope shape."""
    test_case.assertIsInstance(payload, dict, "API payload must be a JSON object.")
    test_case.assertEqual(payload.get("success"), True)
    _assert_field(test_case, payload, "data")
    assert_standard_meta(test_case, payload)


def assert_error_envelope(test_case, payload, expected_code=None):
    """Assert the standard error envelope shape."""
    test_case.assertIsInstance(payload, dict, "API payload must be a JSON object.")
    test_case.assertEqual(payload.get("success"), False)
    error = _assert_field(test_case, payload, "error")
    for field in ERROR_FIELDS:
        _assert_field(test_case, payload, f"error.{field}")
    test_case.assertIsInstance(error["code"], str)
    test_case.assertIsInstance(error["message"], str)
    test_case.assertIsInstance(error["details"], dict)
    test_case.assertIsInstance(error["field_errors"], dict)
    if expected_code == "PERMISSION_DENIED":
        expected_code = "FORBIDDEN"
    if expected_code is not None:
        test_case.assertEqual(error["code"], expected_code)
    assert_standard_meta(test_case, payload)


def assert_pagination_shape(test_case, payload):
    """Assert the top-level list pagination contract."""
    assert_success_envelope(test_case, payload)
    pagination = _assert_field(test_case, payload, "pagination")
    for field in PAGINATION_FIELDS:
        _assert_field(test_case, payload, f"pagination.{field}")
    for field in ("page", "page_size", "total_count", "total_pages"):
        test_case.assertIsInstance(pagination[field], int)
    for field in ("has_next", "has_previous"):
        test_case.assertIsInstance(pagination[field], bool)


def assert_available_actions_shape(test_case, available_actions):
    """Assert the target §44 available_actions item shape for detail endpoints."""
    test_case.assertIsInstance(available_actions, list)
    for index, action in enumerate(available_actions):
        test_case.assertIsInstance(
            action,
            dict,
            f"available_actions[{index}] must be an object.",
        )
        for field in AVAILABLE_ACTION_FIELDS:
            test_case.assertIn(
                field,
                action,
                f"Missing contract field: available_actions[{index}].{field}",
            )
        test_case.assertIsInstance(action["action_code"], str)
        test_case.assertIsInstance(action["label"], str)
        test_case.assertIsInstance(action["enabled"], bool)
        test_case.assertTrue(
            action["disabled_reason"] is None
            or isinstance(action["disabled_reason"], str)
        )
        test_case.assertIsInstance(action["required_permission"], str)

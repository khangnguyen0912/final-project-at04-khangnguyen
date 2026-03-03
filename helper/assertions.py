async def assert_status_code(res, expected_status: int, case_name: str = ""):
    actual_status = res.status
    assert actual_status == expected_status, (
        f"[{case_name}] Expected status {expected_status}, "
        f"but got {actual_status} | {await res.text()}"
    )


async def assert_success_message(res, expected_msg: str):
    body = await res.json()
    assert body.get("msg") == expected_msg, (
        f"Expected msg '{expected_msg}', but got '{body.get('msg')}'"
    )


def assert_field_updated(after_data: dict, field_name: str, expected_value):
    assert after_data.get(field_name) == expected_value, (
        f"Expected '{field_name}' = '{expected_value}', "
        f"but got '{after_data.get(field_name)}'"
    )


def assert_other_fields_unchanged(after: dict, before: dict, fields: list[str]):
    for field in fields:
        assert after.get(field) == before.get(field), (
            f"Field '{field}' changed: "
            f"before='{before.get(field)}', after='{after.get(field)}'"
        )


async def assert_validation_error(res, field_name: str, expected_error_msg: str):
    body = await res.json()

    assert body.get("msg") == "Invalid data.", (
        f"Expected 'Invalid data.' but got '{body.get('msg')}'"
    )

    fields = body.get("fields", {})
    field_error = fields.get(field_name)

    if isinstance(field_error, list):
        field_error = field_error[0]

    assert expected_error_msg in str(field_error), (
        f"Expected error '{expected_error_msg}' in '{field_error}'"
    )
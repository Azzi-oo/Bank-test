import pytest

from src.main.api.steps.admin_steps import AdminSteps


def clean_user(objects: list[int], admin_steps: AdminSteps) -> None:
    errors = []
    for user_id in reversed(list(dict.fromkeys(objects))):
        try:
            admin_steps.delete_user(user_id)
        except Exception as error:
            errors.append(error)
    objects.clear()
    if errors:
        raise ExceptionGroup("Failed to delete users created by this test", errors)


@pytest.fixture
def created_obj(admin_api):
    objects = admin_api.created_objects
    try:
        yield objects
    finally:
        clean_user(objects, admin_api.admin_steps)

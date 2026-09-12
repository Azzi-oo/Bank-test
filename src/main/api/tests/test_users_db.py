import allure
import pytest

from src.main.api.config import USER_PASSWORD
from src.main.api.models.requests import CreateUserRequest, UserRole


@allure.epic("Bank API")
@allure.feature("Пользователи")
@allure.story("Сохранение в PostgreSQL")
@allure.parent_suite("API-тесты")
@allure.suite("Пользователи — БД")
@pytest.mark.api
@pytest.mark.db
class TestUsersDb:
    @allure.title("Созданный через API пользователь сохранён в БД")
    def test_created_user_is_persisted(self, user_db, admin_steps, username):
        with allure.step("Проверить отсутствие пользователя до создания"):
            assert user_db.get_user_by_username(username) is None
        user = admin_steps.create_user(CreateUserRequest(
            username=username, password=USER_PASSWORD, role=UserRole.USER,
        ))
        with allure.step("Сравнить запись в БД с ответом API"):
            saved = user_db.get_user_by_username(username)
            assert saved is not None
            assert saved.id == user.id
            assert saved.username == user.username
            assert saved.role == user.role
            assert saved.deleted_at is None

    @allure.title("Удаление через API отмечает пользователя удалённым в БД")
    def test_deleted_user_is_soft_deleted(self, user_db, admin_steps, create_user_request):
        name = create_user_request.username
        saved = user_db.get_user_by_username(name)
        assert saved is not None
        assert saved.deleted_at is None
        admin_steps.delete_user(saved.id)
        with allure.step("Проверить отметку удаления в БД"):
            deleted = user_db.get_user_by_username(name)
            assert deleted is not None
            assert deleted.deleted_at is not None

    @allure.title("Отклонённый API пользователь не попадает в БД")
    def test_invalid_user_is_not_persisted(self, user_db, admin_steps, username):
        assert user_db.get_user_by_username(username) is None
        admin_steps.create_invalid_user({
            "username": username, "password": "short", "role": UserRole.USER.value,
        })
        with allure.step("Проверить отсутствие записи после HTTP 400"):
            assert user_db.get_user_by_username(username) is None

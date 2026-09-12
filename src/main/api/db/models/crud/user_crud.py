import allure
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.main.api.db.models.user_tabs import User
from src.main.api.reporting import attach_json


class UserCrudDb:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str) -> User | None:
        """Возвращает запись, включая логически удалённую, с актуальными данными."""
        with allure.step("БД: найти пользователя по имени"):
            user = self.db.scalars(
                select(User).where(User.username == username)
                .execution_options(populate_existing=True)
            ).one_or_none()
            attach_json("Пользователь в БД", None if user is None else {
                "id": user.id, "username": user.username, "role": user.role,
                "deleted_at": user.deleted_at,
            })
            return user

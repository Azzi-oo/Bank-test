from sqlalchemy import Column, Integer, String, DateTime

from src.main.api.db.base import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"User(id={self.id!r}, username={self.username!r})"

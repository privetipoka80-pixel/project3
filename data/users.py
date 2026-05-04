import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(
        sqlalchemy.String, unique=True, nullable=False)
    email = sqlalchemy.Column(
        sqlalchemy.String, index=True, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    role = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='user')
    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime, default=datetime.datetime.now)

    products = sqlalchemy.orm.relationship(
        "Product", back_populates="seller", cascade="all, delete-orphan")

    # ДОБАВИТЬ ЭТИ ДВЕ СТРОКИ:
    reviews = sqlalchemy.orm.relationship(
        "Review", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User> {self.id} - {self.username} ({self.role})'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_seller(self):
        return self.role == 'seller'

    def is_user(self):
        return self.role == 'user'

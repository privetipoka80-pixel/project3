import sqlalchemy as sa
from data.db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin 


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    username = sa.Column(sa.String, nullable=True, unique=True)
    email = sa.Column(sa.String, nullable=True, unique=True)
    hashed_password = sa.Column(sa.String, nullable=True)
    role = sa.Column(sa.String, nullable=True, default='user')
    created_at = sa.Column(sa.DateTime, default=sa.func.now())
    products = sa.orm.relationship("Product", back_populates="seller", cascade="all, delete-orphan")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def is_seller(self):
        return self.role == 'seller'

    def is_user(self):
        return self.role == 'user'

    def is_admin(self):
        return self.role == 'admin'

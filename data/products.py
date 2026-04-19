import sqlalchemy as sa
from data.db_session import SqlAlchemyBase

class Product(SqlAlchemyBase):
    __tablename__ = 'products'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=True)
    description = sa.Column(sa.Text, nullable=True)
    price = sa.Column(sa.Float, nullable=True)
    category = sa.Column(sa.String, nullable=True)
    stock = sa.Column(sa.Integer, nullable=True, default=0)
    seller_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    created_at = sa.Column(sa.DateTime, default=sa.func.now())
    seller = sa.orm.relationship("User", back_populates="products")
    images = sa.orm.relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")

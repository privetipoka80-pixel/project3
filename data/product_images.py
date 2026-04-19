import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class ProductImage(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'product_images'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    product_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("products.id"),
                                   nullable=False)
    image_url = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    is_main = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    sort_order = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    product = sqlalchemy.orm.relationship("Product", back_populates="images")

    def __repr__(self):
        return f'<ProductImage> {self.id} - Product {self.product_id}'
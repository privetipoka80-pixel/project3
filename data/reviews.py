import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Review(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'reviews'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    product_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("products.id"),
                                   nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"),
                                nullable=False)
    rating = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    comment = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime, default=datetime.datetime.now)

    product = sqlalchemy.orm.relationship("Product", back_populates="reviews")
    user = sqlalchemy.orm.relationship("User", back_populates="reviews")

    def __repr__(self):
        return f'<Review> {self.id} - Product {self.product_id} - Rating {self.rating}'

    @property
    def username(self):
        return self.user.username if self.user else "Unknown"

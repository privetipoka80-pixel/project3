import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Order(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"),
                                nullable=False)
    product_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("products.id"),
                                   nullable=False)
    quantity = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    total_price = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String, default='pending')
    order_date = sqlalchemy.Column(
        sqlalchemy.DateTime, default=datetime.datetime.now)

    user = sqlalchemy.orm.relationship("User", back_populates="orders")
    product = sqlalchemy.orm.relationship("Product", back_populates="orders")

    def __repr__(self):
        return f'<Order> {self.id} - User {self.user_id} - Product {self.product_id}'

    @property
    def status_name(self):
        statuses = {
            'pending': 'Pending',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        }
        return statuses.get(self.status, self.status)

import datetime
import sqlalchemy as sa
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Product(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'products'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    price = sa.Column(sa.Float, nullable=False)
    category = sa.Column(sa.String, nullable=True)
    stock = sa.Column(sa.Integer, default=0)
    seller_id = sa.Column(
        sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.now)

    seller = sa.orm.relationship("User", back_populates="products")
    images = sa.orm.relationship(
        "ProductImage", back_populates="product", cascade="all, delete-orphan")
    reviews = sa.orm.relationship(
        "Review", back_populates="product", cascade="all, delete-orphan")

    @property
    def main_image(self):
        if self.images:
            main = [img for img in self.images if img.is_main]
            return main[0].image_url if main else self.images[0].image_url
        return None

    @property
    def average_rating(self):
        if not self.reviews:
            return 0
        return sum(r.rating for r in self.reviews) / len(self.reviews)

    @property
    def reviews_count(self):
        return len(self.reviews)

    @property
    def seller_name(self):
        return self.seller.username if self.seller else "Unknown"

    def __repr__(self):
        return f'<Product> {self.id} - {self.name} ({self.price} RUB)'

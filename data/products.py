import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin

class Product(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    seller_id = sqlalchemy.Column(sqlalchemy.Integer, 
                                  sqlalchemy.ForeignKey("users.id"),
                                  nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    category = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    stock = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    
    seller = sqlalchemy.orm.relationship("User", back_populates="products")
    reviews = sqlalchemy.orm.relationship("Review", back_populates="product", cascade="all, delete-orphan")
    orders = sqlalchemy.orm.relationship("Order", back_populates="product", cascade="all, delete-orphan")
    images = sqlalchemy.orm.relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Product> {self.id} - {self.name} ({self.price} RUB)'
    
    @property
    def seller_name(self):
        return self.seller.username if self.seller else "Unknown"
    
    @property
    def main_image(self):
        if self.images:
            main = [img for img in self.images if img.is_main]
            return main[0].image_url if main else self.images[0].image_url
        return None
    
    @property
    def all_images(self):
        return sorted(self.images, key=lambda x: x.sort_order)
    
    @property
    def average_rating(self):
        if not self.reviews:
            return 0
        return sum(r.rating for r in self.reviews) / len(self.reviews)
    
    @property
    def reviews_count(self):
        return len(self.reviews)
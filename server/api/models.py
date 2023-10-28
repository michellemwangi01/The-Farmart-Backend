from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from sqlalchemy import MetaData, UniqueConstraint, ForeignKey
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from api import generate_password_hash

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String)
    username = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    address = db.Column(db.String)
    phone_number = db.Column(db.String)
    email = db.Column(db.String)
    password_hash = db.Column(db.String)
    profile_pic = db.Column(db.String(255))
    isAdmin = db.Column(db.Boolean,default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    orders = db.relationship('Order', back_populates='user', cascade='all, delete-orphan')
    cart = db.relationship('Cart', back_populates='user', cascade='all, delete-orphan')

    __table_args__ = (UniqueConstraint('username', name='user_unique_constraint'),)

    def __repr__(self):
        return f'(id={self.id}, name={self.username} email={self.email} profile_pic={self.profile_pic})'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Vendor(db.Model):
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    fullnames = db.Column(db.String)
    business_name = db.Column(db.String)
    mobile_number = db.Column(db.String)
    email_address = db.Column(db.String)
    physical_address = db.Column(db.String)
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    product_list = db.Column(db.String)
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    products = db.relationship('Product', back_populates='vendor', cascade='all, delete-orphan')
    orders = association_proxy('products', 'orders')

    
    
    def __repr__(self):
        return f'(id={self.id}, businessName={self.business_name} email={self.email_address} mobile_number={self.mobile_number} product_list={self.product_list} )'

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    price = db.Column(db.Numeric(precision=10, scale=2))
    vendor_id = db.Column(db.Integer, ForeignKey('vendors.id', ondelete='CASCADE'))
    category_id = db.Column(db.Integer, ForeignKey('categories.id', ondelete='CASCADE'))
    image = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    __table_args__ = (UniqueConstraint('name', name='product_name_unique_constraint'),)

    vendor = db.relationship('Vendor', back_populates='products')
    category = db.relationship('Category', back_populates='products')
    orders = db.relationship('Order', back_populates='product', cascade='all, delete-orphan')

    def __repr__(self):
        return f'(id={self.id}, name={self.name} description={self.description} price={self.price} price={self.image} user_id={self.user_id} category_id={self.category_id} )'

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    image = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    __table_args__ = (UniqueConstraint('name', name='category_name_unique_constraint'),)

    products = db.relationship('Product', back_populates='category', cascade='all, delete-orphan')

    def __repr__(self):
        return f'(id={self.id}, name={self.name})'

class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    user = db.relationship('User', back_populates='cart', uselist=False)
    cartItems = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')

    def __repr__(self):
        return f'(id={self.id}, user_id={self.user_id})'

class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer)
    added_at = db.Column(db.DateTime, server_default=db.func.now())

    cart = db.relationship('Cart', back_populates='cartItems')
    product = db.relationship('Product')

    def __repr__(self):
        return f'(id={self.id}, cart_id={self.cart_id}, product_id={self.product_id}, quantity={self.quantity})'

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    purchased_at = db.Column(db.DateTime, server_default=db.func.now())
    quantity = db.Column(db.Integer)
    status = db.Column(db.String)
    order_date = db.Column(db.DateTime, server_default=db.func.now())
    
    
    product = db.relationship('Product', back_populates='orders')
    user = db.relationship('User', back_populates='orders')


    @validates('cart_item')
    def validate_cart_item(self, key, cart_item):
        if cart_item.product.vendor_id == self.user_id:
            raise ValueError("You cannot buy your own product.")
        return cart_item


    def __repr__(self):
        return f'(id={self.id}, product_id={self.product_id}, user_id={self.user_id}, purchased_at={self.purchased_at})'

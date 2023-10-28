from api import jsonify, request, url_for,  Resource, User, SQLAlchemyError, make_response,  \
     send_from_directory,  Migrate, db, Api,  \
   Namespace, Marshmallow, fields, check_password_hash, datetime, uuid
from api import app, ma, api
from .api_models import *
from .models import Category, User, Cart, CartItem, Product, Vendor,Order
import os
from functools import wraps
from marshmallow.exceptions import ValidationError
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required


ns = Namespace('snapstore')
api.add_namespace(ns)


def verify_jwt_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            get_jwt_identity()
            return func(*args, **kwargs)
        except Exception as e:
            return {'message': 'Unauthorized'}, 401
    return wrapper






@ns.route('/signup')
class Signup(Resource):
    @ns.expect(user_input_schema)
    @ns.marshal_with(user_schema)
    def post(self):
        data = request.get_json()
        # print("signup",data)
        if data['password'] == data['repeatPassword']:
            if data:
                new_user = User(
                    username=data['username'],
                    email=data['email'],
                    public_id=str(uuid.uuid4())
                )
                new_user.set_password(data['password'])
                print(f'new user:{new_user}')
                new_user.set_password(data['password'])
                db.session.add(new_user)
                db.session.commit()
                print("new added user",new_user)
                return new_user, 201
            else:
                return {'message': "No data found"}, 404
        else:
            return {'message': "No data found"}, 404
        

            #**********GET********
# Vendor routes

# Get a list of all vendors
@ns.route('/vendors')
class VendorList(Resource):
    @ns.marshal_list_with(vendor_schema)
    def get(self):
        vendors = Vendor.query.all()
        return vendors

# Get a single vendor by ID
@ns.route('/vendors/<int:id>')
class VendorResource(Resource):
    @ns.marshal_with(vendor_schema)
    def get(self, id):
        vendor = Vendor.query.get_or_404(id)
        return vendor

# Products routes

# Get a list of all products
@ns.route('/products')
class ProductList(Resource):
    @ns.marshal_list_with(product_schema)
    def get(self):
        products = Product.query.all()
        return products

# Get a single product by ID
@ns.route('/products/<int:id>')
class ProductResource(Resource):
    @ns.marshal_with(product_schema)
    def get(self, id):
        product = Product.query.get_or_404(id)
        return product

# Categories routes

# Get a list of all categories
@ns.route('/categories')
class CategoryList(Resource):
    @ns.marshal_list_with(category_schema)
    def get(self):
        categories = Category.query.all()
        return categories

# Get a single category by ID
@ns.route('/categories/<int:id>')
class CategoryResource(Resource):
    @ns.marshal_with(category_schema)
    def get(self, id):
        category = Category.query.get_or_404(id)
        return category

# Orders routes

# Get a list of all orders
@ns.route('/orders')
class OrderList(Resource):
    @ns.marshal_list_with(order_schema)
    def get(self):
        orders = Order.query.all()
        return orders

# Get a single order by ID
@ns.route('/orders/<int:id>')
class OrderResource(Resource):
    @ns.marshal_with(order_schema)
    def get(self, id):
        order = Order.query.get_or_404(id)
        return order

# Carts routes

# Get a list of all carts
@ns.route('/carts')
class CartList(Resource):
    @ns.marshal_list_with(cart_schema)
    def get(self):
        carts = Cart.query.all()
        return carts

# Get a single cart by ID
@ns.route('/carts/<int:id>')
class CartResource(Resource):
    @ns.marshal_with(cart_schema)
    def get(self, id):
        cart = Cart.query.get_or_404(id)
        return cart

# Cart_items routes

# Get a list of all cart items
@ns.route('/cart_items')
class CartItemList(Resource):
    @ns.marshal_list_with(cart_item_schema)
    def get(self):
        cart_items = CartItem.query.all()
        return cart_items

# Get a single cart item by ID
@ns.route('/cart_items/<int:id>')
class CartItemResource(Resource):
    @ns.marshal_with(cart_item_schema)
    def get(self, id):
        cart_item = CartItem.query.get_or_404(id)
        return cart_item


            #*********POST**********
@ns.route('/users')
class Users(Resource):
    @ns.expect(user_input_schema)
    @ns.marshal_with(user_schema, code=201)
    def post(self):
        data = request.get_json()
        # Validation and processing logic
        new_user = User(
            username=data['username'],
            email=data['email'],
            public_id=str(uuid.uuid4())
        )
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return new_user, 201
    

@ns.route('/vendors')
class Vendors(Resource):
    @ns.expect(vendor_input_schema)
    @ns.marshal_with(vendor_schema, code=201)
    def post(self):
        data = request.get_json()
        # Validation and processing logic
        new_vendor = Vendor(
            user_id=data['user_id'],
            fullnames=data['fullnames'],
            business_name=data['business_name'],
            mobile_number=data['mobile_number'],
            email_address=data['email_address'],
            physical_address=data['physical_address'],
            map_location=data['map_location'],
            product_list=data['product_list'],
            image=data['image']
        )
        db.session.add(new_vendor)
        db.session.commit()
        return new_vendor, 201


@ns.route('/categories')
class Categories(Resource):
    @ns.expect(category_input_schema)
    @ns.marshal_with(category_schema, code=201)
    def post(self):
        data = request.get_json()
        # Validation and processing logic
        new_category = Category(
            name=data['name']
        )
        db.session.add(new_category)
        db.session.commit()
        return new_category, 201


@ns.route('/carts')
class Carts(Resource):
    @ns.marshal_with(cart_schema, code=201)
    def post(self):
        new_cart = Cart()
        db.session.add(new_cart)
        db.session.commit()
        return new_cart, 201


@ns.route('/cart_items')
class CartItems(Resource):
    @ns.expect(cart_item_input_schema)
    @ns.marshal_with(cart_item_schema, code=201)
    def post(self):
        data = request.get_json()
        photo_id = data.get('photo_id')
        quantity = data.get('quantity')

        # Validate that the photo with the given ID exists
        photo = photo.query.get(photo_id)
        if not photo:
            return {'message': 'Photo not found'}, 404

        # Create a new cart item
        new_cart_item = CartItem(
            photo_id=photo_id,
            quantity=quantity
        )

        db.session.add(new_cart_item)
        db.session.commit()

        return new_cart_item, 201


@ns.route('/products')
class Products(Resource):
    @ns.expect(product_input_schema)
    @ns.marshal_with(product_schema, code=201)
    def post(self):
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        vendor_id = data.get('vendor_id')
        category_id = data.get('category_id')
        image = data.get('image')

        # Validate that the vendor and category with the given IDs exist
        vendor = Vendor.query.get(vendor_id)
        category = Category.query.get(category_id)

        if not vendor:
            return {'message': 'Vendor not found'}, 404

        if not category:
            return {'message': 'Category not found'}, 404

        # Create a new product
        new_product = Product(
            name=name,
            description=description,
            price=price,
            vendor_id=vendor_id,
            category_id=category_id,
            image=image
        )

        db.session.add(new_product)
        db.session.commit()

        return new_product, 201


@ns.route('/orders')
class Orders(Resource):
    @ns.expect(order_input_schema)
    @ns.marshal_with(order_schema, code=201)
    def post(self):
        data = request.get_json()
        product_id = data.get('product_id')
        cart_item_id = data.get('cart_item_id')
        user_id = data.get('user_id')
        quantity = data.get('quantity')
        status = data.get('status')

        # Validate that the product, cart item, and user with the given IDs exist
        product = Product.query.get(product_id)
        cart_item = CartItem.query.get(cart_item_id)
        user = User.query.get(user_id)

        if not product:
            return {'message': 'Product not found'}, 404

        if not cart_item:
            return {'message': 'Cart Item not found'}, 404

        if not user:
            return {'message': 'User not found'}, 404

        # Create a new order
        new_order = Order(
            product_id=product_id,
            cart_item_id=cart_item_id,
            user_id=user_id,
            quantity=quantity,
            status=status
        )

        db.session.add(new_order)
        db.session.commit()

        return new_order, 201



            #*********DELETE********
# Delete a vendor
@ns.route('/vendors/<int:id>')
class VendorResource(Resource):
    @ns.marshal_with(vendor_schema)
    def get(self, id):
        vendor = Vendor.query.get_or_404(id)
        return vendor

    @ns.response(204, 'Vendor deleted')
    def delete(self, id):
        vendor = Vendor.query.get_or_404(id)
        db.session.delete(vendor)
        db.session.commit()
        return '', 204

# Products routes

# Delete a product
@ns.route('/products/<int:id>')
class ProductResource(Resource):
    @ns.marshal_with(product_schema)
    def get(self, id):
        product = Product.query.get_or_404(id)
        return product

    @ns.response(204, 'Product deleted')
    def delete(self, id):
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        return '', 204

# Categories routes

# Delete a category
@ns.route('/categories/<int:id>')
class CategoryResource(Resource):
    @ns.marshal_with(category_schema)
    def get(self, id):
        category = Category.query.get_or_404(id)
        return category

    @ns.response(204, 'Category deleted')
    def delete(self, id):
        category = Category.query.get_or_404(id)
        db.session.delete(category)
        db.session.commit()
        return '', 204

# Orders routes

# Delete an order
@ns.route('/orders/<int:id>')
class OrderResource(Resource):
    @ns.marshal_with(order_schema)
    def get(self, id):
        order = Order.query.get_or_404(id)
        return order

    @ns.response(204, 'Order deleted')
    def delete(self, id):
        order = Order.query.get_or_404(id)
        db.session.delete(order)
        db.session.commit()
        return '', 204

# Carts routes

# Delete a cart
@ns.route('/carts/<int:id>')
class CartResource(Resource):
    @ns.marshal_with(cart_schema)
    def get(self, id):
        cart = Cart.query.get_or_404(id)
        return cart

    @ns.response(204, 'Cart deleted')
    def delete(self, id):
        cart = Cart.query.get_or_404(id)
        db.session.delete(cart)
        db.session.commit()
        return '', 204

# Cart_items routes

# Delete a cart item
@ns.route('/cart_items/<int:id>')
class CartItemResource(Resource):
    @ns.marshal_with(cart_item_schema)
    def get(self, id):
        cart_item = CartItem.query.get_or_404(id)
        return cart_item

    @ns.response(204, 'Cart item deleted')
    def delete(self, id):
        cart_item = CartItem.query.get_or_404(id)
        db.session.delete(cart_item)
        db.session.commit()
        return '', 204


            #**********PUT &PATCH*******

#category
@ns.route('/categories/<int:id>')
class CategoryResource(Resource):
    @ns.expect(category_input_schema)
    @ns.marshal_with(category_schema)
    def put(self, id):
        # Update a category by ID using request data
        category = Category.query.get_or_404(id)
        data = request.get_json()
        category.name = data.get('name')
        db.session.commit()
        return category

    @ns.expect(category_input_schema)
    @ns.marshal_with(category_schema)
    def patch(self, id):
        # Partially update a category by ID using request data
        category = Category.query.get_or_404(id)
        data = request.get_json()
        if 'name' in data:
            category.name = data.get('name')
        db.session.commit()
        return category

@ns.route('/users/<int:id>')
class UserResource(Resource):
    @ns.expect(user_input_schema)
    @ns.marshal_with(user_schema)
    def put(self, id):
        # Update a user by ID using request data
        user = User.query.get_or_404(id)
        data = request.get_json()
        user.username = data.get('username')
        user.email = data.get('email')
        # Update other user fields as needed
        db.session.commit()
        return user

    @ns.expect(user_input_schema)
    @ns.marshal_with(user_schema)
    def patch(self, id):
        # Partially update a user by ID using request data
        user = User.query.get_or_404(id)
        data = request.get_json()
        if 'username' in data:
            user.username = data.get('username')
        if 'email' in data:
            user.email = data.get('email')
        # Update other user fields as needed
        db.session.commit()
        return user


#carts
@ns.route('/carts/<int:id>')
class CartResource(Resource):
    @ns.marshal_with(cart_schema)
    def put(self, id):
        # Update a cart by ID (e.g., not typically updated)
        cart = Cart.query.get_or_404(id)
        # Update cart properties as needed
        db.session.commit()
        return cart
# Additional routes for handling specific use cases or edge-cases may be added here...

@ns.route('/cart_items/<int:id>')
class CartItemResource(Resource):
    @ns.expect(cart_item_input_schema)
    @ns.marshal_with(cart_item_schema)
    def put(self, id):
        # Update a cart item by ID using request data
        cart_item = CartItem.query.get_or_404(id)
        data = request.get_json()
        cart_item.photo_id = data.get('photo_id')
        cart_item.quantity = data.get('quantity')
        db.session.commit()
        return cart_item

    @ns.expect(cart_item_input_schema)
    @ns.marshal_with(cart_item_schema)
    def patch(self, id):
        # Partially update a cart item by ID using request data
        cart_item = CartItem.query.get_or_404(id)
        data = request.get_json()
        if 'photo_id' in data:
            cart_item.photo_id = data.get('photo_id')
        if 'quantity' in data:
            cart_item.quantity = data.get('quantity')
        db.session.commit()
        return cart_item


@ns.route('/products/<int:id>')
class ProductResource(Resource):
    @ns.expect(product_input_schema)
    @ns.marshal_with(product_schema)
    def put(self, id):
        # Update a product by ID using request data
        product = Product.query.get_or_404(id)
        data = request.get_json()
        product.name = data.get('name')
        product.description = data.get('description')
        product.price = data.get('price')
        product.vendor_id = data.get('vendor_id')
        product.category_id = data.get('category_id')
        product.image = data.get('image')
        db.session.commit()
        return product

    @ns.expect(product_input_schema)
    @ns.marshal_with(product_schema)
    def patch(self, id):
        # Partially update a product by ID using request data
        product = Product.query.get_or_404(id)
        data = request.get_json()
        if 'name' in data:
            product.name = data.get('name')
        # Update other product fields as needed
        db.session.commit()
        return product

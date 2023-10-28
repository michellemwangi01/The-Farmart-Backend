from api import jsonify, request, url_for,  Resource, User, SQLAlchemyError, make_response,  \
     send_from_directory,  Migrate, db, Api,  \
   Namespace, Marshmallow, fields, check_password_hash, datetime, uuid
from api import app, ma, api
from .api_models import *
from .models import Category, User, Cart, CartItem, Product, Vendor,Order
import os
from functools import wraps
from marshmallow.exceptions import ValidationError
from flask_uploads import UploadSet, configure_uploads, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, get_jwt_identity, jwt_required



ns = Namespace('home')
ns_vendor = Namespace('vendors')
ns_user = Namespace('users')
ns_category = Namespace('categories')
ns_product = Namespace('products')
ns_cart = Namespace('cart')
ns_cartitem = Namespace('cart items')
ns_order = Namespace('orders')
api.add_namespace(ns)
api.add_namespace(ns_cart)
api.add_namespace(ns_cartitem)
api.add_namespace(ns_category)
api.add_namespace(ns_order)
api.add_namespace(ns_product)
api.add_namespace(ns_user)
api.add_namespace(ns_vendor)
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
jwt = JWTManager(app)




# ----------------------------------------------  V E N D O R   R O U T E S-----------------------------------------------
# Delete a vendor
@ns_vendor.route('/vendors/<int:id>')
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
    

@ns_vendor.route('/vendors')
class Vendors(Resource):
    @ns.marshal_list_with(vendor_schema)
    def get(self):
        vendors = Vendor.query.all()
        return vendors

    @ns.expect(vendor_schema)
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
            latitude=data['map_location'],
            product_list=data['product_list'],
            image=data['image']
        )
        db.session.add(new_vendor)
        db.session.commit()
        return new_vendor, 201
    
    @ns.expect(vendor_input_schema)
    @ns.marshal_with(vendor_schema)
    def put(self, id):
        # Update a vendor by ID using request data
        vendor = Vendor.query.get_or_404(id)
        data = request.get_json()
        vendor.user_id = data.get('user_id')
        vendor.fullnames = data.get('fullnames')
        vendor.business_name = data.get('business_name')
        vendor.mobile_number = data.get('mobile_number')
        vendor.email_address = data.get('email_address')
        vendor.physical_address = data.get('physical_address')
        vendor.map_location = data.get('map_location')
        vendor.product_list = data.get('product_list')
        vendor.image = data.get('image')
        db.session.commit()
        return vendor

    @ns.expect(vendor_input_schema)
    @ns.marshal_with(vendor_schema)
    def patch(self, id):
        # Partially update a vendor by ID using request data
        vendor = Vendor.query.get_or_404(id)
        data = request.get_json()
        if 'user_id' in data:
            vendor.user_id = data.get('user_id')
        # Update other vendor fields as needed
        db.session.commit()
        return vendor


# ----------------------------------------------  P R O D U C T S   R O U T E S -----------------------------------------------


@ns_product.route('/products')
class Products(Resource):
    @ns.marshal_list_with(product_schema)
    def get(self):
        products = Product.query.all()
        return products
    

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



@ns_product.route('/products/<int:id>')
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
    


# ----------------------------------------------  C A T E G O R I E S  R O U T E S -----------------------------------------------

@ns_category.route('/categories')
class Categories(Resource):
    @ns.marshal_list_with(category_schema)
    def get(self):
        categories = Category.query.all()
        return categories
    
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


@ns_category.route('/categories/<int:id>')
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
    

# ----------------------------------------------  O R D E R S   R O U T E S -----------------------------------------------
#  !!missing post route!!

@ns_order.route('/orders')
class OrderList(Resource):
    @ns.marshal_list_with(order_schema)
    def get(self):
        orders = Order.query.all()
        return orders


@ns_order.route('/orders/<int:id>')
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

    @ns.expect(order_input_schema)
    @ns.marshal_with(order_schema)
    def put(self, id):
        # Update an order by ID using request data
        order = Order.query.get_or_404(id)
        data = request.get_json()
        order.product_id = data.get('product_id')
        order.cart_item_id = data.get('cart_item_id')
        order.user_id = data.get('user_id')
        order.quantity = data.get('quantity')
        order.status = data.get('status')
        db.session.commit()
        return order

    @ns.expect(order_input_schema)
    @ns.marshal_with(order_schema)
    def patch(self, id):
        # Partially update an order by ID using request data
        order = Order.query.get_or_404(id)
        data = request.get_json()
        if 'product_id' in data:
            order.product_id = data.get('product_id')
        if 'cart_item_id' in data:
            order.cart_item_id = data.get('cart_item_id')
        if 'user_id' in data:
            order.user_id = data.get('user_id')
        if 'quantity' in data:
            order.quantity = data.get('quantity')
        if 'status' in data:
            order.status = data.get('status')
        db.session.commit()
        return order

    

# ---------------------------------------------- C A R T S   R O U T E S -----------------------------------------------


@ns_cart.route('/carts')
class CartList(Resource):
    @ns.marshal_list_with(cart_schema)
    def get(self):
        carts = Cart.query.all()
        return carts
    
    @ns.expect(carts_output_schema)
    @ns.marshal_with(cart_schema, code=201)
    def post(self):
        new_cart = Cart(
            # check current user and add the cart to them
        )
        db.session.add(new_cart)
        db.session.commit()
        return new_cart, 201


@ns_cart.route('/carts/<int:id>')
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

    @ns.marshal_with(cart_schema)
    def put(self, id):
        # Update a cart by ID (e.g., not typically updated)
        cart = Cart.query.get_or_404(id)
        # Update cart properties as needed
        db.session.commit()
        return cart


  
# ---------------------------------------------- U S E R    R O U T E S -----------------------------------------------
@ns_user.route('/users')
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
    
    # @token_required
    @ns.marshal_list_with(users_schema)
    def get(self):
        # if not current_user.admin:
        #     return jsonify({"message": "Sorry. You are not authorized to perform this function"})
        users = User.query.all()
        return users,200


@ns_user.route('/users/<int:id>')
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
    
    # @token_required
    @ns.response(204, 'User deleted')
    def delete(self, id):
        # if not current_user.admin:
        #     return jsonify({"message": "Sorry. You are not authorized to perform this function"})
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return '', 204



# ---------------------------------------------- C A R T   I T E M   R O U T E S -----------------------------------------------

@ns_cartitem.route('/cart_items')
class CartItems(Resource):
    @ns.expect(cart_item_input_schema)
    @ns.marshal_with(cart_item_schema)
    def post(self):
        data = request.get_json()

        errors = cart_item_input_schema.validate(data)
        if errors:
            return {'message': 'Input data is not valid', 'errors': errors}, 400

        product_id = data.get('product_id')
        quantity = data.get('quantity')
        cart_id = data.get('cart_id')

        # Validate that the product with the given ID exists
        product = Product.query.get(product_id)
        if not product:
            return {'message': 'product not found'}, 404

        # Create a new cart item
        new_cart_item = CartItem(
            product_id=product_id,
            quantity=quantity,
            cart_id = cart_id
        )

        db.session.add(new_cart_item)
        db.session.commit()

        return new_cart_item, 201

    @ns.marshal_list_with(cart_item_schema)
    def get(self):
        cart_items = CartItem.query.all()
        return cart_items


@ns_cartitem.route('/cart_items/<int:id>')
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

    @ns.expect(cart_item_input_schema)
    @ns.marshal_with(cart_item_schema)
    def put(self, id):
        # Update a cart item by ID using request data
        cart_item = CartItem.query.get_or_404(id)
        data = request.get_json()
        cart_item.product_id = data.get('product_id')
        cart_item.quantity = data.get('quantity')
        db.session.commit()
        return cart_item

    @ns.expect(cart_item_input_schema)
    @ns.marshal_with(cart_item_schema)
    def patch(self, id):
        # Partially update a cart item by ID using request data
        cart_item = CartItem.query.get_or_404(id)
        data = request.get_json()
        if 'product_id' in data:
            cart_item.product_id = data.get('product_id')
        if 'quantity' in data:
            cart_item.quantity = data.get('quantity')
        db.session.commit()
        return cart_item
    

# ---------------------------------------------- I M A G E  U P L O A D S   R O U T E S -----------------------------------------------

class UploadForm(FlaskForm):
    photo = FileField(
        validators=[
            FileAllowed(photos, 'Only images are allowed'),
            FileRequired('File field should not be empty')]
    )
    submit = SubmitField('Upload')

class GetFile(Resource):
    def get(self, filename):
        return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)

api.add_resource(GetFile, '/uploads/<filename>')
    
# @ns.route('/uploadimage')
class UploadImage(Resource):
    def post(self):
        try:
            file = request.files["image"]
            if file:
                # filename = photos.save(form.photo.data)  # Save the image to the uploads folder
                # file_url = url_for('get_file', filename=filename)
                filename = os.path.join(app.config["UPLOADED_PHOTOS_DEST"], file.filename)
                file.save(filename)
                return make_response(jsonify(filename), 200)
            else:
                return {"message": "No file uploaded"}, 400
        except Exception as e:
            return {"message error": str(e)}, 500

api.add_resource(UploadImage, '/uploadimage')


@app.route('/photos/<path:filename>')
def get_image(filename):
    return send_from_directory('photos', filename)




# ---------------------------------------------- A U T H E N T I C A T I O N   R O U T E S -----------------------------------------------

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
        if data['password'] == data['repeatpassword']:
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
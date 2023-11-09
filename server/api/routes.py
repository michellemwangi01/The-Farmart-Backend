
from api import jsonify, request, url_for,  Resource, User, make_response, send_from_directory,   db,   \
   Namespace,  check_password_hash,  uuid
from api import app, api
from .api_models import *
from .models import Category, User, Cart, CartItem, Product, Vendor,Order, Payment , UploadedImage, OrderProducts
import os
from functools import wraps  
from flask_uploads import UploadSet, configure_uploads, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, get_jwt_identity, jwt_required, current_user
from flask import url_for
from datetime import  timedelta


photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
jwt = JWTManager(app)
jwt.init_app(app)


authorizations = {
    "jwToken":{
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user


@jwt.user_lookup_loader
def user_lookup_callback(__jwt__header, jwt_data):
    identity = jwt_data['sub']
    return User.query.filter_by(id=identity).first()


ns_auth = Namespace('authorization', description='Authorization related operations', authorizations=authorizations)
ns_payment = Namespace('payments', description='Payment related operations',authorizations=authorizations)
ns_vendor = Namespace('vendors', description='Vendor related operations',authorizations=authorizations)
ns_user = Namespace('users', description='User & Payment related operations',authorizations=authorizations)
ns_category = Namespace('categories', description='Category related operations',authorizations=authorizations)
ns_product = Namespace('products', description='Product related operations',authorizations=authorizations)
ns_cart = Namespace('cart', description='Cart related operations',authorizations=authorizations)
ns_cartitem = Namespace('cartitems', description='CartItem related operations',authorizations=authorizations)
ns_order = Namespace('orders', description='Product Order related operations', authorizations=authorizations)

api.add_namespace(ns_auth)
api.add_namespace(ns_payment)
api.add_namespace(ns_cart)
api.add_namespace(ns_cartitem)
api.add_namespace(ns_category)
api.add_namespace(ns_order)
api.add_namespace(ns_product)
api.add_namespace(ns_user)
api.add_namespace(ns_vendor)


# ----------------------------------------------------- G L O B A L  V A R I A B L E S -----------------------------------------------


paymentConfirmationDetails = []
print(paymentConfirmationDetails)

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


@ns_auth.route('/signup')
class Signup(Resource):
    @ns.expect(signup_input_schema)
    # @ns.marshal_with(users_schema)
    def post(self):
        data = request.get_json()
        print("signup",data)
        if not data:
            return {"message":"Data not found!"},404
        
        required_fields = ['username', 'email', 'password', 'repeatpassword', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data or data[field]=='':
                return {'message': f'Missing required field: {field}'}, 400
            
        if data['password'] != data['repeatpassword']:
            return {'message': "Passwords Do No Match"}, 404
        
        new_user = User(
            username=data['username'],
            email=data['email'],
            public_id=str(uuid.uuid4()),
            first_name = data['first_name'],
            last_name = data['last_name'],
        )      
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        print("new added user",new_user)

        user_dict = {
            key: getattr(new_user,key)
            for key in ["id","username", "email", "public_id", "first_name", "last_name"]
        }

        # create cart for user
        new_cart = Cart(
            user_id = new_user.id
        )
        db.session.add(new_cart)
        db.session.commit()
        return user_dict, 201


@ns_auth.route('/login')
class Login(Resource):
    @ns.expect(user_login_schema)
    def post(self):
        data = request.get_json()

        if not data or not data['username'] or not data['password']:
            return {'message': 'Unable to verify user'}, 401

        user = User.query.filter_by(email=data['username']).first()

        if not user:
            return {'message': 'Authentication failed. Invalid username or password'}, 401

        vendor = Vendor.query.filter_by(user_id =user.id).first()

        if not vendor:
            vendor_id = None
        else:
            vendor_id = vendor.id

        if check_password_hash(user.password_hash, data['password']):
            access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=30))

            refresh_token = create_refresh_token(identity=user.id,expires_delta=timedelta(days=30))

            response_data = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'current_user':{
                    'fullname': user.first_name +" "+ user.last_name,
                    'firstname': user.first_name ,
                    'lastname': user.last_name,
                    'user_id': user.id,
                    'email':user.email,
                    'profile_pic':user.profile_pic,
                    'vendor_id': vendor_id,
                    'address': user.address,
                    'phone_number': user.phone_number
                }    
            }
            # Check if the user has a cart, if not, create one
            user_cart = Cart.query.filter_by(user_id=user.id).first()
            if not user_cart:
                try:
                    new_cart = Cart(user=user)
                    db.session.add(new_cart)
                    db.session.commit()
                    print(f"Cart created for user {user.id}")
                except Exception as e:
                    db.session.rollback()
                    return {'message': f'Error creating cart for user {user.id}: {str(e)}'}, 500

            return response_data, 201
        else:
            return {'message': 'Invalid credentials'}, 401


# @ns_auth.route('/refresh_token')
# class refreshToken(Resource):
#     method_decorators = [jwt_required(refresh=True)]
#     @ns.doc(security='jwToken')
#     @ns.expect(refresh_token_schema)
#     def post(self):
#         # Extract refresh token from req
#         refresh_token = request.get_json()['refresh_token']

#          # Validate refresh token
#         if not jwt.refresh_token_loader(refresh_token):
#             return jsonify({'error': 'Invalid refresh token'}), 401
        
#         identity = get_jwt_identity()
#         print(identity)
        
#         # Create new access token and refresh token
#         new_access_token = create_access_token(identity=get_jwt_identity())
#         new_refresh_token = create_refresh_token(identity=get_jwt_identity())

        
#         print('---------------------> {current_user}')
#         return jsonify({
#             'access_token': new_access_token,
#             'refresh_token': new_refresh_token,
#             'current_user': current_user               
#         })

#         # access_token = create_access_token(identity=current_user)
#         # return jsonify({'access_token': access_token}), 200


# ----------------------------------------------  P A Y M E N T   R O U T E S -----------------------------------------------

 
@ns_payment.route('/farmartpayment')
class MakePayment(Resource):
    @ns.marshal_with(payments_schema)
    def post(self):
        # TO RUN NGROK SERVER TO POPULATE PAYMENT TABLE: `ngrok http 5555 --domain redfish-prime-pigeon.ngrok-free.app`
        # CHANGE WEBHOOK IN TINYPESA IF DOMAIN CHANGES CURRENT DOMAIN: `redfish-prime-pigeon.ngrok-free.app`
        data = request.get_json()
        if 'Body' in data and 'stkCallback' in data['Body']:
            payment_details = data['Body']['stkCallback']
            if payment_details:
                keys_to_extract = ["ResultCode", "ResultDesc", "CallbackMetadata", "ExternalReference", "Amount", "Msisdn"]
                transaction_data = {
                    key: payment_details.get(key)
                    for key in keys_to_extract
                }
                print("!!!!!!Webhook received and processed successfully!!!!!!!")
                print(f"---------->Data:{transaction_data}")


            #  create payment record
            callback_metadata= transaction_data['CallbackMetadata']['Item']
            for item in callback_metadata:
                if item['Name'] == "Amount":
                    amount = item.get('Value')
                elif item['Name'] == "MpesaReceiptNumber":
                    mpesa_receipt_number = item.get('Value')
                elif item['Name'] == "TransactionDate":
                    transaction_date = item.get('Value')
                elif item['Name'] == "PhoneNumber":
                    phone_number = item.get('Value')

            new_payment = Payment(
                mpesa_receipt_code=mpesa_receipt_number,
                payment_date=transaction_date,
                paid_by_number=phone_number,
                amount_paid=amount,
                payment_uid=transaction_data['ExternalReference']
            )
            db.session.add(new_payment)
            db.session.commit() 

            # update order status with payment confirmed
            orders = Order.query.filter_by(payment_uid=transaction_data['ExternalReference'])
            if orders:
                for order in orders:
                    order.status = 'Payment Received'
                db.session.commit()
                

            return new_payment, 201
        else:
            return {'message': 'Invalid request data'}, 400


@ns_payment.route('/get_payment_confirmation_details')
class GetPaymentConfirmation(Resource):
    @ns.marshal_with(payments_schema)
    def get(self):
        payments = Payment.query.all()
        if payments:
            # print(f'-----------------> {payments}')
            return payments, 200
        else:
            return {'message': 'No payment confirmation data available'}, 404 
        

@ns_payment.route('/payments')
class Payments(Resource):
    def post(self):
        data = request.get_json()
        callback_metadata= data['CallbackMetadata']['Item']
        for item in callback_metadata:
            if item['Name'] == "Amount":
                amount = item.get('Value')
            elif item['Name'] == "MpesaReceiptNumber":
                mpesa_receipt_number = item.get('Value')
            elif item['Name'] == "TransactionDate":
                transaction_date = item.get('Value')
            elif item['Name'] == "PhoneNumber":
                phone_number = item.get('Value')

        new_payment = Payment(
            mpesa_receipt_code=mpesa_receipt_number,
            payment_date=transaction_date,
            paid_by_number=phone_number,
            amount_paid=amount,
            payment_uid=data.get('ExternalReference')  
        )
        db.session.add(new_payment)
        db.session.commit()        

# ----------------------------------------------  V E N D O R   R O U T E S-----------------------------------------------


@ns_vendor.route('/vendors')
class Vendors(Resource):
    @ns.marshal_list_with(vendors_schema)
    def get(self):
        vendors = Vendor.query.all()
        return vendors

    @ns.expect(vendor_input_schema)
    @ns.marshal_with(vendors_schema, code=201)
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
            latitude=data['latitude'],
            longitude=data['longitude'],
            product_list=', '.join(data['category']),
            image=data['image'],
            county=data['county']
        )
        db.session.add(new_vendor)
        db.session.commit()
        return new_vendor, 201
    
  
@ns_vendor.route('/vendors/<int:id>')
class VendorResource(Resource):
    @jwt_required()
    @ns.marshal_with(vendor_schema)
    def get(self, id):
        current_user = get_jwt_identity()
        user = User.query.filter_by(id = current_user).first()
        if user.isAdmin == False:
            return {'message':'You are not allowed to view this page'}, 404
        vendor = Vendor.query.get_or_404(id)
        return vendor
    
    @ns.expect(vendor_input_schema)
    @ns.marshal_with(vendor_schema)
    def put(self, id):
        # Update a vendor by ID using request data
        vendor = Vendor.query.get_or_404(id)
        data = request.get_json()
        for attr in data:
            setattr(vendor, attr, data[attr])
        db.session.commit()
        return vendor

    @ns.expect(vendor_input_schema)
    @ns.marshal_with(vendor_schema)
    def patch(self, id):
        # Partially update a vendor by ID using request data
        vendor = Vendor.query.get_or_404(id)
        data = request.get_json()
        for attr in data:
            setattr(vendor, attr, data[attr])
        # if 'user_id' in data:
        #     vendor.user_id = data.get('user_id')
        # # Update other vendor fields as needed
        db.session.commit()
        return vendor

    # @ns.response(204, 'Vendor deleted')
    def delete(self, id):
        vendor = Vendor.query.get_or_404(id)
        db.session.delete(vendor)
        db.session.commit()
        return {"message":"product successfully deleted"}, 200
    


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


@ns_product.route('/vendor_products')
class ProductResource(Resource):  
    method_decorators = [jwt_required()]
    @ns.doc(security='jwToken')
    @ns.marshal_with(product_schema)
    def get(self):
        vendor = Vendor.query.filter_by(user_id=current_user.id).first()
        if vendor:    
            products = Product.query.filter_by(vendor_id=vendor.id).all()
            return products, 200
        else:
            return {"message": "User is not registered as a vendor and has no products."}


@ns_product.route('/products/<int:id>')
class ProductResource(Resource):  
    @ns.marshal_with(product_schema)
    def get(self, id):
        product = Product.query.get_or_404(id)
        return product

    def delete(self, id):
        product = Product.query.get_or_404(id)
        if product:
            # orders = Order.query.filter(Order.product_id == id).all()
            print("---------------------------------------")
            # print(orders)
        db.session.delete(product)
        db.session.commit()
        return {"message":"product successfully deleted!"}, 200
    


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

    def delete(self, id):
        category = Category.query.get_or_404(id)
        db.session.delete(category)
        db.session.commit()
        return {"message":"product successfully deleted"}, 200
    
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
        for attr in data:
            setattr(category, attr, data[attr])
        db.session.commit()
        return category
    

# ----------------------------------------------  O R D E R S   R O U T E S -----------------------------------------------

@ns_order.route('/orders')
class OrderList(Resource):
    method_decorators = [jwt_required()]
    # @ns.doc(security='jwToken')
    @ns.marshal_list_with(order_schema)
    def get(self):
        orders = Order.query.all()
        return orders

    @ns.doc(security='jwToken')
    @ns.expect(order_input_schema)
    @ns.marshal_with(order_schema)
    def post(self):
        data = request.get_json()
        new_order = Order(
            user_id = current_user.id,
            status=data['status'],
            payment_uid = data['payment_uid'],
            delivery_type = data['delivery_type'],
            phone_number = data['phone_number'],
            shipping_address = data['shipping_address'],
            email = data['email'],
            county = data['county'],
            amount = data['amount'],
            full_name = data['FullName'],
        )
        db.session.add(new_order)
        db.session.commit()
        return new_order, 201

@ns_order.route('/product_orders')  
class OrderProductsResource(Resource):
    @ns.expect(order_products_schema)
    @ns.marshal_with(order_products_schema)    
    def post(self):
        data = request.get_json() 
        # print(data)
        new_order_product = OrderProducts(
            order_id= data['order_id'],
            product_id= data['product_id'],
            quantity= data['quantity'],
            amount= data['amount'],
            vendor_id = data['vendor_id']
        )
        db.session.add(new_order_product)
        db.session.commit()
        return new_order_product,200


@ns_order.route('/user_orders')
class OrderResource(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security='jwToken')
    @ns.marshal_list_with(order_schema)
    def get(self):
        orders = Order.query.filter_by(user_id=current_user.id).all()
        return orders, 200


@ns_order.route('/vendor_orders')
class VendorOrderResource(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security='jwToken')
    @ns.marshal_with(order_products_schema)
    def get(self):
        vendor = Vendor.query.filter_by(user_id=current_user.id).first()
        # print(vendor)
        if vendor:
            order_products = OrderProducts.query.filter_by(vendor_id=vendor.id).all()
            # print(order_products)
            return order_products, 200
        else:
            return {"message": "User is not a vendor"}


@ns_order.route('/orders/<int:id>')
class OrderResource(Resource):
    @ns.marshal_with(order_schema)
    def get(self, id):
        order = Order.query.get_or_404(id)
        return order

    def delete(self, id):
        order = Order.query.get_or_404(id)
        db.session.delete(order)
        db.session.commit()
        return {"message":"Order successfully deleted"}, 200


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
        return order, 200

    @ns.expect(order_input_schema)
    @ns.marshal_with(order_schema)
    def patch(self, id):
        # Partially update an order by ID using request data
        order = Order.query.get_or_404(id)
        data = request.get_json()
        for attr in data:
            setattr(order, attr, data[attr])
        db.session.commit()
        return order, 200




# ---------------------------------------------- C A R T S   R O U T E S -----------------------------------------------


@ns_cart.route('/carts')
class CartList(Resource):
    @ns.marshal_list_with(cart_schema)
    def get(self):
        carts = Cart.query.all()
        return carts
    
    @ns.expect(carts_input_schema)
    @ns.marshal_with(carts_input_schema, code=201)
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

    def delete(self, id):
        cart = Cart.query.get_or_404(id)
        db.session.delete(cart)
        db.session.commit()
        return {"message":"Cart successfully deleted"}, 200


    @ns.marshal_with(carts_input_schema)
    def put(self, id):
        # Update a cart by ID (e.g., not typically updated)
        cart = Cart.query.get_or_404(id)
        # Update cart properties as needed
        db.session.commit()
        return cart


  
# ---------------------------------------------- U S E R    R O U T E S -----------------------------------------------
@ns_user.route('/users')
class Users(Resource):
    method_decorators = [jwt_required()]
    @ns.expect(user_input_schema)
    @ns.marshal_with(users_schema, code=201)
    def post(self):
        data = request.get_json()

        new_user = User(
            username=data['username'],
            email=data['email'],
            public_id=str(uuid.uuid4())
        )
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()

        # create cart for user
        new_cart = Cart(
            user_is = new_user.id
        )
        db.session.add(new_cart)
        db.session.commit()
        return new_user, 201
    
    @ns.doc(security='jwToken')
    @ns.marshal_list_with(users_schema)
    def get(self):
        users = User.query.all()
        return users,200


    # @ns.marshal_with(user_schema)
    # def get(self, id):
    #     user = User.query.get_or_404(id)
    #     return user
    
    @ns.expect(user_input_schema)
    @ns.marshal_with(users_schema)
    def put(self, id):
        user = User.query.get_or_404(id)
        data = request.get_json()
        user.username = data.get('username')
        user.email = data.get('email')
        db.session.commit()
        return user

    
    @ns.expect(user_input_schema)
    @ns.marshal_with(users_schema)
    @ns.doc(security='jwToken')
    def patch(self):
        print(current_user)
        user = User.query.get_or_404(current_user.id)
        data = request.get_json()
        print(f'------------------------------RECEIVED USER UPDATES: {data}')

        for attr in data:
            setattr(user, attr, data[attr])      
        db.session.add(user) 
        db.session.commit()
        print(f'------------------------------NEW USER: {user}')
        return user
    
    # @token_required
    # @ns.response(204, 'User deleted')
    def delete(self, id):
        # if not current_user.admin:
        #     return jsonify({"message": "Sorry. You are not authorized to perform this function"})
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return {"message":"User successfully deleted"}, 200




# ---------------------------------------------- C A R T   I T E M   R O U T E S -----------------------------------------------

@ns_cartitem.route('/cart_items')
class CartItems(Resource):
    method_decorators = [jwt_required()]
    @ns.expect(cart_item_input_schema)
    @ns.marshal_with(cart_item_schema)
    @ns.doc(security='jwToken')
    def post(self):
        data = request.get_json()
        # print(data)
        errors = cart_item_input_schema.validate(data)
        if errors:
            return {'message': 'Input data is not valid', 'errors': errors}, 400

        product_id = data.get('product_id')
        quantity = data.get('quantity')
        

        # Validate that the product with the given ID exists
        product = Product.query.get_or_404(product_id)
        if not product:
            return {'message': 'product not found'}, 404
        
        # Validate that the user exists and get the Cart ID 
        user = User.query.get_or_404(current_user.id)
        if user:
            cart = Cart.query.filter_by(user_id = user.id).first()
            # print(cart)
            if cart:
                new_cart_item = CartItem(
                    product_id=product_id,
                    quantity=quantity,
                    cart_id = cart.id
                    )
                # print(new_cart_item)
                db.session.add(new_cart_item)
                db.session.commit()
                return new_cart_item, 201
            else:
                return {'message': 'Cart not found'}, 404
        else:
            return {'message': 'User not found'}, 404

        # Create a new cart item
        

    @ns.marshal_list_with(cart_item_schema)
    def get(self):
        cart_items = CartItem.query.all()
        return cart_items

@ns_cartitem.route('/clear_cart_items')
class ClearCartItemResource(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security='jwToken')
    def delete(self):
        # user_id = request.get_json()['user_id']
        print('----------------------- current user id: {current_user.id}')
        user_cart = Cart.query.filter(Cart.user_id == current_user.id).first()

        if user_cart:
            user_cart_id = user_cart.id
            CartItem.query.filter(CartItem.cart_id == user_cart_id).delete()
            
        
            db.session.commit()
            
            return {"message": "Cart successfully cleared"}, 200
        else:
            return {"message": "User not found."}, 404



@ns_cartitem.route('/user_cart_items')
class CIR(Resource):
    method_decorators = [jwt_required()]

    @ns.marshal_with(cart_item_schema)

    @ns.doc(security='jwToken')
    def get(self):
        print(f'----------------------- current user id: {current_user.id}')
        user_cart = Cart.query.filter(Cart.user_id == current_user.id).first()
        if user_cart:
            user_cart_id = user_cart.id
            cart_items = CartItem.query.filter(CartItem.cart_id == user_cart_id).all()
            return cart_items,200
        else:
            return {"message":"The user was not found."}
        

    @jwt_required()
    # @ns.expect(cart_delete_schema)
    @ns.marshal_with(cart_item_schema)
    def delete(self):
        current_user_id = get_jwt_identity()
        data = request.get_json()
        # print(data)
        current_user_id = get_jwt_identity()
    
        print('----------------------- current user id: {current_user_id}')
        user_cart = Cart.query.filter(Cart.user_id == current_user_id).first()
        if user_cart:
            user_cart_id = user_cart.id
            CartItem.query.filter(CartItem.cart_id == user_cart_id).delete()
            return {"message":"Cart Successfully cleared"},200
        else:
            return {"message":"The user was not found."}, 404
        

    @jwt_required()
    @ns.marshal_with(cart_item_schema)
    def post(self):
        data = request.get_json()
        current_user_id = get_jwt_identity()
        print('----------------------- current user id: {current_user_id}')
        user_cart = Cart.query.filter(Cart.user_id == current_user_id).first()
        if user_cart:
            user_cart_id = user_cart.id
            new_cart_item = CartItem(
                product_id=data['product_id'],
                quantity=data["quantity"],
                cart_id = user_cart_id
        )
            new_cart_item.save()
            return new_cart_item,200
        else:
            return {"message":"The user was not found."}
        
        
@ns_cartitem.route('/cart_items/<int:id>')
class CartItemResource(Resource):
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
        cart_item = CartItem.query.get_or_404(id)
        data = request.get_json()
        for attr in data:
            setattr(cart_item, attr, data[attr])
        db.session.commit()
        product = Product.query.filter_by(id = cart_item.product_id).first()
        cart_item.amount = product.price * cart_item.quantity
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
                filename = os.path.join(app.config["UPLOADED_PHOTOS_DEST"], file.filename)
                file.save(filename)
                base_url = request.url_root 
                image_url = url_for('get_image', filename=file.filename)
                complete_url = base_url + image_url

                uploaded_image = UploadedImage(filename=file.filename, url=complete_url)
                db.session.add(uploaded_image)
                db.session.commit()

                return make_response(jsonify({"url": complete_url}), 200)
            else:
                return {"message": "No file uploaded"}, 400
        except Exception as e:
            return {"message error": str(e)}, 500

api.add_resource(UploadImage, '/uploadimage')


@app.route('/photos/<path:filename>')
def get_image(filename):
    return send_from_directory('photos', filename)




   
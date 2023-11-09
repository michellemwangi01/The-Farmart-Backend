from api import fields, api, ma, CartItem
from marshmallow import Schema, fields
from flask_restx import Api,Resource,Namespace,fields

ns = Namespace('farmart')
api.add_namespace(ns)

# ------------------------- A P I _ M O D E L S ------------------------

users_summary_schema = api.model('users',{
    "public_id": fields.String,
    "username": fields.String,
    "email": fields.String,
    "profile_pic": fields.String
    
})

users_schema = api.model('users',{
    "public_id": fields.String,
    "username": fields.String,
    "email": fields.String,
    "first_name": fields.String,
    "last_name": fields.String,
    "address": fields.String,
    "phone_number": fields.String,
    "profile_pic": fields.String,
})




user_input_schema = api.model('user_input',{
    "username": fields.String,
    "password": fields.String,
    "repeatpassword": fields.String,
    "email": fields.String,
    "profile_pic": fields.String,
    "first_name": fields.String,
    "last_name": fields.String,
    "address": fields.String,
    "phone_number": fields.String,
})

signup_input_schema = api.model('signup_input',{
    "username": fields.String,
    "password": fields.String,
    "repeatpassword": fields.String,
    "email": fields.String,
    "first_name": fields.String,
    "last_name": fields.String,
    
})

user_login_schema = api.model('user_login',{
    "username": fields.String,
    "password": fields.String,

})

category_input_schema = api.model('category_input',{
    "name": fields.String,
    'image': fields.String
})



photo_category_schema = api.model('photo_category',{
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "price": fields.Integer,
    "image": fields.String,
})

transaction_schema = api.model('transaction', {
    "id": fields.Integer,
    "photo": fields.Nested(photo_category_schema),
    "user": fields.Nested(users_schema),
    "purchased_at": fields.DateTime,
})



category_schema = api.model('category',{
    "id": fields.Integer,
    "name": fields.String,
    "image": fields.String,
    "products": fields.List(fields.Nested(photo_category_schema))
})
categories_schema = api.model('categories',{
    "id": fields.Integer,
    "name": fields.String,
})



cart_item_input_schema = api.model('cart_item_input', {
    "product_id": fields.Integer,
    "quantity": fields.Integer,
    "cart_id": fields.Integer
    
})

transaction_input_schema = api.model('transaction_input', {
    "product_id": fields.Integer(required=True),
    "quantity": fields.Integer(required=True),
})


transaction_input_schema = api.model('transaction_input', {
    "id": fields.Integer,
})



carts_output_schema = api.model('carts_output',{
    "id": fields.Integer,
    "user_id":fields.Integer,
    "created_at": fields.DateTime,
    "updated_at": fields.DateTime

})

carts_input_schema = api.model('carts_input',{
    "id": fields.Integer,
    "user_id":fields.Integer,

})

vendor_input_schema = api.model('vendor_input',{
    "user_id" : fields.Integer, 
    "fullnames" :fields.String,
    "business_name" :fields.String,
    "mobile_number" :fields.String,
    "email_address" : fields.String,
    "physical_address" : fields.String,
    "latitude" : fields.Float,
    "longitude" : fields.Float,
    "product_list" : fields.String,
    "image" : fields.String,

})

vendors_schema=api.model('vendors',{
    "id":fields.Integer,
    "user_id" : fields.Integer,
    "fullnames" :fields.String,
    "business_name" :fields.String,
    "mobile_number" :fields.String,
    "email_address" : fields.String,
})


product_input_schema = api.model('product_input', {
    "name": fields.String,
    "description": fields.String,
    "vendor_id": fields.Integer,
    "category_id": fields.Integer,
    "image": fields.String,
    "price": fields.Integer,
    
})

vendor_order_schema =  api.model('vendor_order',{
   "id":fields.Integer,
    "user_id" : fields.Integer, 
    "fullnames" :fields.String,
    "business_name" :fields.String,
    "mobile_number" :fields.String,
    "email_address" : fields.String,
    "physical_address" : fields.String,
    "latitude" : fields.Float,
    "longitude" : fields.Float,
    "product_list" : fields.String,
    "image" : fields.String,
    "county": fields.String,
    "created_at" : fields.DateTime,
    "updated_at" : fields.DateTime, 
})
product_summary_schema = api.model("products_order", {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "image": fields.String,
    "price": fields.Integer,
    "product_id": fields.Integer,
    "vendor": fields.Nested(vendor_order_schema),
    "category": fields.Nested(categories_schema),
})
cart_item_output_schema = api.model('cart_item_output', {
    "id": fields.Integer,
    "cart_id": fields.Integer,
    "product": fields.Nested(product_summary_schema),
    "quantity": fields.Integer,
    "added_at": fields.DateTime,
})

cart_item_schema = api.model('cart_item', {
    "id": fields.Integer,
    "cart_id": fields.Integer,
    "product_id": fields.Integer,
    "quantity": fields.Integer,
    "added_at": fields.DateTime,
    "product": fields.Nested(product_summary_schema),
    "amount": fields.Integer,
})



order_input_schema = api.model('order_input', {
    "product_id": fields.Integer,
    "user_id": fields.Integer,
    "quantity": fields.Integer,
    "status": fields.String,
    "delivery_type" :fields.String,
    "phone_number" : fields.String,
    "shipping_address" : fields.String,
    "county" : fields.String,
    "email" :fields.String,
    "amount" : fields.Integer,
    "payment_uid" : fields.String,
    "full_name": fields.String,
    "vendor_id": fields.Integer,
    "DoorStepDelivery": fields.String,
    "Pickup": fields.String,

})
product_schema = api.model("products", {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "image": fields.String,
    "price": fields.Integer,
    "category_id": fields.Integer,
    "vendor": fields.Nested(vendor_order_schema),
    "category": fields.Nested(category_input_schema),
    "created_at": fields.DateTime
    
})


payments_schema = api.model('payments',{
    'id':fields.Integer,
    'mpesa_receipt_code':fields.String,
    'payment_date':fields.String,
    'paid_by_number':fields.String,
    'amount_paid':fields.Integer,
    'payment_uid':fields.String,
    # 'order':fields.Nested(order_products_schema)
})

order_schema = api.model('order', {
    "id": fields.Integer,
    "user_id": fields.Integer,
    "quantity": fields.Integer,
    "status": fields.String,
    "delivery_type" :fields.String,
    "phone_number" : fields.String,
    "shipping_address" : fields.String,
    "county" : fields.String,
    "email" :fields.String,
    "amount" : fields.Integer,
    "date_created" :fields.DateTime,
    "payment_uid" : fields.String,
    "products": fields.List(fields.Nested(product_schema)),
    "user": fields.Nested(users_summary_schema),
    'payment': fields.Nested(payments_schema),
   
  
})


user_schema = api.model('user',{
    "public_id": fields.String,
    "username": fields.String,
    "email": fields.String,
    "first_name": fields.String,
    "first_name": fields.String,
    "address": fields.String,
    "phone_number": fields.String,
     "profile_pic": fields.String,
     "orders": fields.List(fields.Nested(order_schema))
})
vendor_schema=api.model('vendor',{
    "id":fields.Integer,
    "user_id" : fields.Integer, 
    "fullnames" :fields.String,
    "business_name" :fields.String,
    "mobile_number" :fields.String,
    "email_address" : fields.String,
    "physical_address" : fields.String,
    "latitude" : fields.Float,
    "longitude" : fields.Float,
    "product_list" : fields.String,
    "image" : fields.String,
    "created_at" : fields.DateTime,
    "updated_at" : fields.DateTime, 
    "products": fields.List(fields.Nested(product_schema)),
    "orders": fields.List(fields.Nested(order_schema))
})

cart_schema=api.model('cart',{
    "id": fields.Integer,
    "user_id": fields.Integer,
    "cartItems": fields.List(fields.Nested(cart_item_output_schema)),
})


UploadImage_schema=api.model('UploadImage',{
    "id": fields.Integer,
    "filename": fields.String,
    "url":fields.String
})

cart_delete_schema = api.model('cart_delete_schema',{

})
product_order_schema = api.model('product_order_schema',{
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "image": fields.String,
    "price": fields.Integer,
    "category_id": fields.Integer,
    "category": fields.Nested(category_input_schema),
    "created_at": fields.DateTime
})

order_products_schema = api.model('order_products_schema',{
    'id': fields.Integer,
    'product_id': fields.Integer,
    'vendor_id': fields.Integer,
    'order_id': fields.Integer,
    'quantity': fields.Integer,
    'amount': fields.Integer,
    'products': fields.Nested(product_order_schema),
    'orders': fields.Nested(order_schema),
    'vendor': fields.Nested(vendor_order_schema),
    'payment': fields.Nested(payments_schema),
})

refresh_token_schema = api.model('refresh_token_schema',{
    "refresh_token": fields.String
})
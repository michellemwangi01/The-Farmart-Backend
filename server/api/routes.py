from api import jsonify, request, url_for,  Resource, User, SQLAlchemyError, make_response,  \
     send_from_directory,  Migrate, db, Api,  \
   Namespace, Marshmallow, fields, check_password_hash, datetime, uuid
from api import app, ma, api
from .api_models import *
from .models import Category, User, Cart, CartItem, Product, Vendor
from flask_uploads import UploadSet, configure_uploads, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField
import os
from functools import wraps
from marshmallow.exceptions import ValidationError
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, get_jwt_identity, jwt_required


ns = Namespace('farmart')
api.add_namespace(ns)
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
jwt = JWTManager(app)



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
        


@ns.route('/login')
class Login(Resource):
    @ns.expect(user_login_schema)
    def post(self):
        data = request.get_json()

        if not data or not data['username'] or not data['password']:
            return {'message': 'Could Not Verify'}, 401

        user = User.query.filter_by(username=data['username']).first()

        if not user:
            return {'message': 'Could Not Verify'}, 401


        if check_password_hash(user.password_hash, data['password']):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            response_data = {
                'access_token': access_token,
                'username': user.username,
                 'user_id': user.id
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
            return jsonify({'message': 'Invalid credentials'}), 401


@ns.route('/categories')      
class Categories(Resource):
    @ns.marshal_with(categories_schema)
    def get(self):
        categories = Category.query.all()
        for category in categories:
            category.image_path = url_for('static', filename='photos/live_animals.jpg')
        image_path = url_for('static', filename = 'photos/live_animals.jpg'),
        print(image_path)
        return categories, 200
    

@ns.route('/users')
class Users(Resource):
    # @token_required
    @ns.marshal_list_with(users_schema)
    def get(self):
        # if not current_user.admin:
        #     return jsonify({"message": "Sorry. You are not authorized to perform this function"})
        users = User.query.all()
        return users,200

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


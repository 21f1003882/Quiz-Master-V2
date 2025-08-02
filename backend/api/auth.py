# api/auth.py
from flask import request, jsonify, Blueprint
from flask_restful import Api, Resource, reqparse
from flasgger import swag_from
from core.extensions import db, csrf
from core.models import User, Role, SecretQuestion
from flask_jwt_extended import create_access_token, jwt_required
import re

auth_api_bp = Blueprint('auth_api', __name__)
api = Api(auth_api_bp)

# --- (Password validation and other classes remain the same) ---
def is_password_strong(password):
    if len(password) < 6: return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[0-9]", password): return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): return False
    return True

class LoginAPI(Resource):
    method_decorators = [csrf.exempt]
    def post(self):
        data = request.get_json()
        username_or_email = data.get('username')
        password = data.get('password')
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if user and user.check_password(password):
            additional_claims = {"roles": [role.name for role in user.roles], "username": user.username}
            access_token = create_access_token(identity=user.fs_uniquifier, additional_claims=additional_claims)
            return {'access_token': access_token}, 200
        return {"message": "Invalid credentials"}, 401

class SecretQuestionsAPI(Resource):
    method_decorators = [csrf.exempt]
    def get(self):
        questions = SecretQuestion.query.all()
        return jsonify([{'id': q.id, 'text': q.text} for q in questions])

class RegisterAPI(Resource):
    method_decorators = [csrf.exempt]
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('secret_question_id', type=int, required=True)
        parser.add_argument('secret_answer', type=str, required=True)
        data = parser.parse_args()

        if User.query.filter((User.username == data['username']) | (User.email == data['email'])).first():
            return {"message": "Username or email already exists"}, 400
        if not is_password_strong(data['password']):
            return {"message": "Password is not strong enough."}, 400
        if not SecretQuestion.query.get(data['secret_question_id']):
            return {"message": "Invalid secret question selected"}, 400

        user_role = Role.query.filter_by(name='user').first()
        new_user = User(username=data['username'], email=data['email'], active=True, secret_question_id=data['secret_question_id'])
        new_user.set_password(data['password'])
        new_user.set_secret_answer(data['secret_answer'])
        new_user.roles.append(user_role)
        db.session.add(new_user)
        db.session.commit()

        secret_key_part = '-'.join(new_user.fs_uniquifier.split('-')[1:4])
        additional_claims = {"roles": ["user"], "username": new_user.username}
        access_token = create_access_token(identity=new_user.fs_uniquifier, additional_claims=additional_claims)
        return {'message': 'Registration successful!', 'secret_key': secret_key_part, 'access_token': access_token}, 201


class ForgotPasswordGetQuestionAPI(Resource):
    method_decorators = [csrf.exempt]
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('email', type=str, required=True)
            data = parser.parse_args()
            user = User.query.filter_by(email=data['email']).first()

            if user and user.secret_question:
                return jsonify({
                    'username': user.username,
                    'secret_question': user.secret_question.text
                })
            
            # To prevent user enumeration, we don't return a 404.
            return jsonify({'message': 'If a user with that email exists, the process will continue.'})
        except Exception as e:
            print(f"ERROR in ForgotPasswordGetQuestionAPI: {e}")
            return {'message': 'An internal server error occurred.'}, 500

class ForgotPasswordResetAPI(Resource):
    method_decorators = [csrf.exempt]
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('secret_answer', type=str, required=True)
        parser.add_argument('secret_key', type=str, required=True)
        parser.add_argument('new_password', type=str, required=True)
        data = parser.parse_args()

        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return {'message': 'Invalid details provided. Please try again.'}, 400

        # Check 1: Secret Answer
        if not user.check_secret_answer(data['secret_answer']):
            return {'message': 'Invalid details provided. Please try again.'}, 400
            
        # Check 2: Secret Key (fs_uniquifier)
        secret_key_part = '-'.join(user.fs_uniquifier.split('-')[1:4])
        if data['secret_key'] != secret_key_part:
            return {'message': 'Invalid details provided. Please try again.'}, 400

        # Check 3: New Password Strength
        if not is_password_strong(data['new_password']):
            return {"message": "Your new password is not strong enough."}, 400

        # All checks passed, update the password
        user.set_password(data['new_password'])
        db.session.commit()
        
        return {'message': 'Password has been reset successfully.'}, 200

# --- Register all resources ---
api.add_resource(LoginAPI, '/login')
api.add_resource(SecretQuestionsAPI, '/secret-questions')
api.add_resource(RegisterAPI, '/register')
api.add_resource(ForgotPasswordGetQuestionAPI, '/forgot-password/get-question')
api.add_resource(ForgotPasswordResetAPI, '/forgot-password/reset')
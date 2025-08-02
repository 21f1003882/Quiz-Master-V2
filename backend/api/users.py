from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource, reqparse
from flasgger import swag_from
from core.extensions import db
from core.models import User, Role
from .decorators import admin_required_api # Only admin manages users via API?
from werkzeug.security import generate_password_hash

# Define the Blueprint
users_api_bp = Blueprint('users_api', __name__)
api = Api(users_api_bp)

definitions = {
    "User": {
          "type": "object", "properties": {
              "id": {"type": "integer"}, "username": {"type": "string"}, "email": {"type": "string"},
              "active": {"type": "boolean"}, "created_at": {"type": "string", "format": "date-time"},
              "roles": {"type": "array", "items": {"type": "string"}}
          }
      },
      "UserInput": { # For POST
          "type": "object", "properties": {
              "username": {"type": "string"}, "email": {"type": "string"},
              "password": {"type": "string", "format": "password"},
              "active": {"type": "boolean", "default": True}
              # Add roles if API allows setting roles on create?
          }, "required": ["username", "email", "password"]
      },
      "UserInputOptional": { # For PUT
           "type": "object", "properties": {
              "username": {"type": "string"}, "email": {"type": "string"},
              "active": {"type": "boolean"}
              # Add password/roles if API allows updates?
          }
      },
      "Role": {
          "type": "object", "properties": {
              "id": {"type": "integer"}, "name": {"type": "string"}, "description": {"type": "string", "nullable": True}
          }
      },
      }

class UserListAPI(Resource):
    decorators = [admin_required_api] # Only admin can list/create users via API?
    @swag_from({
        'tags': ['Users'], 'summary': 'List all users (Admin only)',
        'responses': {200: {'description': 'List of users'}} # Add schema
    })
    def get(self):
        users = User.query.all()
        result = [{'id': u.id, 'username': u.username, 'email': u.email, 'active': u.active,
                   'created_at': u.created_at.isoformat()} for u in users]
        return jsonify({'users': result})

    # Be careful with creating users via API vs web registration
    @swag_from({
        'tags': ['Users'], 'summary': 'Create a new user (Admin only)',
        'parameters': [{'name': 'body', 'in': 'body', 'required': True, 'schema': {'$ref': '#/definitions/UserInput'}}],
        'responses': {201: {'description': 'User created'}, 400: {'description': 'Invalid input or user exists'}}
    })
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('active', type=bool, default=True)
        # Add role assignment? Requires role ID/name
        data = parser.parse_args()

        if User.query.filter((User.username == data['username']) | (User.email == data['email'])).first():
            return {'message': 'Username or email already exists'}, 400

        user = User(username=data['username'], email=data['email'], active=data['active'])
        user.password = data['password'] # Uses the password setter from User model
        # Assign default 'user' role?
        user_role = Role.query.filter_by(name='user').first()
        if user_role:
            user.roles.append(user_role)

        db.session.add(user)
        try:
            db.session.commit()
            return {'message': 'User created', 'user': {'id': user.id, 'username': user.username}}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error creating user: {e}'}, 500


class UserDetailAPI(Resource):
    decorators = [admin_required_api] # Only admin can manage users via API?
    @swag_from({
        'tags': ['Users'], 'summary': 'Get details of a specific user (Admin only)',
        'parameters': [{'name': 'user_id', 'in': 'path', 'type': 'integer', 'required': True}],
        'responses': {200: {'description': 'User details'}, 404: {'description': 'User not found'}} # Add schema
    })
    def get(self, user_id):
        user = User.query.get_or_404(user_id, description='User not found')
        roles = [role.name for role in user.roles]
        return jsonify({
            'id': user.id, 'username': user.username, 'email': user.email, 'active': user.active,
            'created_at': user.created_at.isoformat(), 'roles': roles
        })

    @swag_from({
        'tags': ['Users'], 'summary': 'Update a user (Admin only)',
        'parameters': [
            {'name': 'user_id', 'in': 'path', 'type': 'integer', 'required': True},
            {'name': 'body', 'in': 'body', 'required': True, 'schema': {'$ref': '#/definitions/UserInputOptional'}}
        ],
        'responses': {200: {'description': 'User updated'}, 400: {'description': 'Username/email exists'}, 404: {'description': 'User not found'}}
    })
    def put(self, user_id):
        user = User.query.get_or_404(user_id, description='User not found')
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('active', type=bool)
        # Add password change? Role change?
        data = parser.parse_args()

        if data['username'] and data['username'] != user.username:
             if User.query.filter(User.username == data['username'], User.id != user_id).first():
                 return {'message': 'Username already exists'}, 400
             user.username = data['username']
        if data['email'] and data['email'] != user.email:
             if User.query.filter(User.email == data['email'], User.id != user_id).first():
                 return {'message': 'Email already exists'}, 400
             user.email = data['email']
        if data['active'] is not None:
             user.active = data['active']

        try:
            db.session.commit()
            return {'message': 'User updated', 'user': {'id': user.id, 'username': user.username}}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error updating user: {e}'}, 500

    @swag_from({
        'tags': ['Users'], 'summary': 'Delete a user (Admin only)',
        'parameters': [{'name': 'user_id', 'in': 'path', 'type': 'integer', 'required': True}],
        'responses': {200: {'description': 'User deleted'}, 404: {'description': 'User not found'}}
    })
    def delete(self, user_id):
        user = User.query.get_or_404(user_id, description='User not found')
        # Prevent admin from deleting themselves? Or last admin? Add checks if needed.
        try:
            db.session.delete(user)
            db.session.commit()
            return {'message': 'User deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error deleting user: {e}'}, 500
        
users_api_bp.add_app_template_global(definitions, name='user_definitions')
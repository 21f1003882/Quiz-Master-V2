from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource, reqparse
from flasgger import swag_from
from core.extensions import db
from core.models import QuizAttempt, User, Quiz
from .decorators import admin_required_api
from datetime import datetime, timezone
from flask_login import current_user
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from utils import parse_datetime

definitions = {
    "Attempt": {
          "type": "object", "properties": {
              "id": {"type": "integer"}, "user_id": {"type": "integer"}, "quiz_id": {"type": "integer"},
              "score": {"type": "integer"}, "total_questions": {"type": "integer"},
              "start_time": {"type": "string", "format": "date-time"},
              "submitted_at": {"type": "string", "format": "date-time", "nullable": True},
              "percentage_score": {"type": "number", "format": "float"}
          }
      },
      "AttemptInput": { # For POST
          "type": "object", "properties": {
              "user_id": {"type": "integer"}, "quiz_id": {"type": "integer"},
              "score": {"type": "integer"}, "total_questions": {"type": "integer"},
              "start_time": {"type": "string", "format": "date-time", "nullable": True},
              "submitted_at": {"type": "string", "format": "date-time", "nullable": True}
          }, "required": ["user_id", "quiz_id", "score", "total_questions"]
      },
      "AttemptInputOptional": { # For PUT
           "type": "object", "properties": {
              "score": {"type": "integer"}, "total_questions": {"type": "integer"},
              "submitted_at": {"type": "string", "format": "date-time", "nullable": True}
          }
      },
}

# Define the Blueprint
attempts_api_bp = Blueprint('attempts_api', __name__)
api = Api(attempts_api_bp)

class QuizAttemptListAPI(Resource):
    method_decorators = {'get': [jwt_required()], 'post': [admin_required_api, jwt_required()]}
    @swag_from({
         'tags': ['Attempts'], 'summary': 'List quiz attempts (filtered by user/quiz)',
         'parameters': [
             {'name': 'user_id', 'in': 'query', 'type': 'integer', 'required': False, 'description': 'Filter by user ID (admin only)'},
             {'name': 'quiz_id', 'in': 'query', 'type': 'integer', 'required': False, 'description': 'Filter by quiz ID'}
         ],
        'responses': {200: {'description': 'List of quiz attempts', 'schema': {'$ref': '#/definitions/AttemptListResponse'}}}
    })
    def get(self):
        query = QuizAttempt.query
        user_id_filter = request.args.get('user_id', type=int)
        quiz_id_filter = request.args.get('quiz_id', type=int)

        # Non-admins can only see their own attempts
        if not jwt_current_user.has_role('admin'):
            query = query.filter_by(user_id=jwt_current_user.id)
            if user_id_filter and user_id_filter != jwt_current_user.id:
                 return {'message': 'Forbidden'}, 403 
        elif user_id_filter:
            # Admin provided a user_id filter
             query = query.filter_by(user_id=user_id_filter)

        if quiz_id_filter:
            query = query.filter_by(quiz_id=quiz_id_filter)

        attempts = query.order_by(QuizAttempt.start_time.desc()).all()
        result = [{
            'id': a.id, 'user_id': a.user_id, 'quiz_id': a.quiz_id, 'score': a.score,
            'total_questions': a.total_questions, 
            'start_time': a.start_time.isoformat() if a.start_time else None, 
            'submitted_at': a.submitted_at.isoformat() if a.submitted_at else None,
            'percentage_score': a.percentage_score
            } for a in attempts]
        return jsonify({'attempts': result})

    
    @swag_from({
         'tags': ['Attempts'], 'summary': 'Record a quiz attempt (Admin Only)',
         'parameters': [{'name': 'body', 'in': 'body', 'required': True, 'schema': {'$ref': '#/definitions/AttemptInput'}}],
         'responses': {201: {'description': 'Quiz attempt recorded'}, 400:{}, 404:{}, 500:{}}
    })

    def post(self):
         parser = reqparse.RequestParser()
         parser.add_argument('user_id', type=int, required=True)
         parser.add_argument('quiz_id', type=int, required=True)
         parser.add_argument('score', type=int, required=True)
         parser.add_argument('total_questions', type=int, required=True)
         parser.add_argument('start_time', type=str) 
         parser.add_argument('submitted_at', type=str)
         data = parser.parse_args()

         if not User.query.get(data['user_id']): return {'message': 'User not found'}, 404
         if not Quiz.query.get(data['quiz_id']): return {'message': 'Quiz not found'}, 404

         start_dt = parse_datetime(data.get('start_time')) or datetime.now(timezone.utc) # Use helper, default to now
         submit_dt = parse_datetime(data.get('submitted_at')) # Use helper

         attempt = QuizAttempt(
            user_id=data['user_id'], quiz_id=data['quiz_id'], score=data['score'],
            total_questions=data['total_questions'],
            start_time=start_dt,
            submitted_at=submit_dt
         )
         db.session.add(attempt)
         try:
            db.session.commit()
            return {'message': 'Quiz attempt recorded', 'attempt': {'id': attempt.id}}, 201
         except Exception as e:
             db.session.rollback(); print(f"Error recording attempt: {e}")
             return {'message': f'Error recording attempt'}, 500



class QuizAttemptDetailAPI(Resource):
    @jwt_required()
    @swag_from({
         'tags': ['Attempts'], 'summary': 'Get details of a specific quiz attempt',
         'parameters': [{'name': 'attempt_id', 'in': 'path', 'type': 'integer', 'required': True}],
         'responses': {200: {'description': 'Attempt details', 'schema': {'$ref': '#/definitions/Attempt'}}, 404: {}, 403: {}}
    })
    def get(self, attempt_id):
        attempt = QuizAttempt.query.get_or_404(attempt_id, description='Attempt not found')
        # Check permissions: Admin or owner of the attempt
        if not jwt_current_user.has_role('admin') and attempt.user_id != jwt_current_user.id:
            return {'message': 'Forbidden'}, 403
        return jsonify({
             'id': attempt.id, 'user_id': attempt.user_id, 'quiz_id': attempt.quiz_id, 'score': attempt.score,
             'total_questions': attempt.total_questions,
             'start_time': attempt.start_time.isoformat() if attempt.start_time else None,
             'submitted_at': attempt.submitted_at.isoformat() if attempt.submitted_at else None,
             'percentage_score': attempt.percentage_score
        })

    @jwt_required()
    @admin_required_api # Requires @jwt_required implicitly via decorator chain or apply both
    @jwt_required() # Apply JWT check first explicitly
    @swag_from({
        'tags': ['Attempts'], 'summary': 'Update a quiz attempt (Admin Only)',
         'parameters': [
            {'name': 'attempt_id', 'in': 'path', 'type': 'integer', 'required': True},
            {'name': 'body', 'in': 'body', 'required': True, 'schema': {'$ref': '#/definitions/AttemptInputOptional'}}
        ],
        'responses': {200: {'description': 'Attempt updated'}, 404: {}, 500:{}}
    })
    def put(self, attempt_id):
        attempt = QuizAttempt.query.get_or_404(attempt_id, description='Attempt not found')
        parser = reqparse.RequestParser()
        parser.add_argument('score', type=int)
        parser.add_argument('total_questions', type=int)
        parser.add_argument('submitted_at', type=str)
        data = parser.parse_args()

        if data['score'] is not None: attempt.score = data['score']
        if data['total_questions'] is not None: attempt.total_questions = data['total_questions']
        if data['submitted_at'] is not None: attempt.submitted_at = parse_datetime(data['submitted_at'])

        try:
            db.session.commit()
            return {'message': 'Quiz attempt updated', 'attempt': {'id': attempt.id}}, 200
        except Exception as e:
            db.session.rollback(); print(f"Error updating attempt: {e}")
            return {'message': f'Error updating attempt'}, 500

    @jwt_required()
    @admin_required_api # Requires @jwt_required implicitly via decorator chain or apply both
    @jwt_required() # Apply JWT check first explicitly
    @swag_from({
        'tags': ['Attempts'], 'summary': 'Delete a quiz attempt (Admin Only)',
        'parameters': [{'name': 'attempt_id', 'in': 'path', 'type': 'integer', 'required': True}],
        'responses': {200: {'description': 'Attempt deleted'}, 404: {}, 500:{}}
    })
    def delete(self, attempt_id):
        attempt = QuizAttempt.query.get_or_404(attempt_id, description='Attempt not found')
        try:
            db.session.delete(attempt)
            db.session.commit()
            return {'message': 'Quiz attempt deleted successfully'}, 200
        except Exception as e:
            db.session.rollback(); print(f"Error deleting attempt: {e}")
            return {'message': f'Error deleting attempt'}, 500
        
api.add_resource(QuizAttemptListAPI, '/')
api.add_resource(QuizAttemptDetailAPI, '/<int:attempt_id>')

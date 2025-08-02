from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource, reqparse
from flasgger import swag_from
from core.extensions import db
from core.models import Quiz, Chapter, Subject 
from .decorators import admin_required_api
from datetime import datetime 
from flask_jwt_extended import jwt_required
from utils import parse_datetime

# Define the Blueprint
quizzes_api_bp = Blueprint('quizzes_api', __name__)
api = Api(quizzes_api_bp)



class QuizListAPI(Resource):
    # Apply decorators per method
    @jwt_required()
    @swag_from({
        'tags': ['Quizzes'], 'summary': 'Get a list of all quizzes',
         'parameters': [
             {'name': 'chapter_id', 'in': 'query', 'type': 'integer', 'required': False, 'description': 'Filter by chapter ID'}
        ],
        'responses': {200: {'description': 'A list of quizzes', 'schema': {'$ref': '#/definitions/QuizListResponse'}}}
    })
    def get(self):
        query = Quiz.query
        chapter_id = request.args.get('chapter_id', type=int)
        if chapter_id:
            query = query.filter_by(chapter_id=chapter_id)

        # Join to get related names for response clarity
        quizzes = query.join(Chapter).join(Subject).order_by(Subject.name, Chapter.name, Quiz.title).all()
        result = [{
            'id': q.id, 'title': q.title, 'chapter_id': q.chapter_id,
            'chapter_name': q.chapter.name, # Added for context
            'subject_name': q.chapter.subject.name, # Added for context
            'duration_minutes': q.duration_minutes,
            'scheduled_date': q.scheduled_date.isoformat() if hasattr(q, 'scheduled_date') and q.scheduled_date else None, # Check attribute exists
            'is_active': q.is_active
        } for q in quizzes]
        return jsonify({'quizzes': result})

    @jwt_required() # Apply both decorators
    @jwt_required()
    @admin_required_api
    @swag_from({
        'tags': ['Quizzes'], 'summary': 'Create a new quiz',
        'parameters': [{'name': 'body', 'in': 'body', 'required': True, 'schema': {'$ref': '#/definitions/QuizInput'}}],
        'responses': { 201: {'description': 'Quiz created', 'schema': {'$ref': '#/definitions/Quiz'}}, 400: {}, 404: {}, 500: {} }
    })
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True, help='Title cannot be blank')
        parser.add_argument('chapter_id', type=int, required=True, help='Chapter ID cannot be blank')
        parser.add_argument('duration_minutes', type=int, required=True, help='Duration cannot be blank')
        parser.add_argument('scheduled_date', type=str) # Optional ISO string
        parser.add_argument('is_active', type=bool, default=True)
        data = parser.parse_args()

        if not Chapter.query.get(data['chapter_id']):
             return {'message': f'Chapter with id {data["chapter_id"]} not found'}, 404

        parsed_scheduled_date = parse_datetime(data.get('scheduled_date'))

        quiz = Quiz(
            title=data['title'],
            chapter_id=data['chapter_id'],
            duration_minutes=data['duration_minutes'],
            scheduled_date=parsed_scheduled_date, # Use parsed date
            is_active=data['is_active']
        )
        db.session.add(quiz)
        try:
            db.session.commit()
            # Return full quiz details on creation, including related names
            return {
                 'id': quiz.id, 'title': quiz.title, 'chapter_id': quiz.chapter_id,
                 'chapter_name': quiz.chapter.name, # Add related names
                 'subject_name': quiz.chapter.subject.name, # Add related names
                 'duration_minutes': quiz.duration_minutes,
                 'scheduled_date': quiz.scheduled_date.isoformat() if quiz.scheduled_date else None,
                 'is_active': quiz.is_active
            }, 201
        except Exception as e:
            db.session.rollback(); print(f"Error creating quiz: {e}")
            return {'message': f'Error creating quiz'}, 500

class QuizDetailAPI(Resource):
    method_decorators = {
        'get': [jwt_required()],
        'put': [admin_required_api, jwt_required()],
        'delete': [admin_required_api, jwt_required()]
    }

    @swag_from({
        'tags': ['Quizzes'], 'summary': 'Get details of a specific quiz',
        'parameters': [{'name': 'quiz_id', 'in': 'path', 'type': 'integer', 'required': True}],
        'responses': { 200: {'description': 'Quiz details', 'schema': {'$ref': '#/definitions/Quiz'}}, 404: {} }
    })
    def get(self, quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        return jsonify({
            'id': quiz.id, 'title': quiz.title, 'chapter_id': quiz.chapter_id,
            'chapter_name': quiz.chapter.name, # Add related names
            'subject_name': quiz.chapter.subject.name, # Add related names
            'duration_minutes': quiz.duration_minutes,
            'scheduled_date': quiz.scheduled_date.isoformat() if hasattr(quiz, 'scheduled_date') and quiz.scheduled_date else None,
            'is_active': quiz.is_active
        })

    @swag_from({
        'tags': ['Quizzes'], 'summary': 'Update an existing quiz',
         'parameters': [
            {'name': 'quiz_id', 'in': 'path', 'type': 'integer', 'required': True},
            {'name': 'body', 'in': 'body', 'required': True, 'schema': {'$ref': '#/definitions/QuizInputOptional'}}
        ],
        'responses': { 200: {'description': 'Quiz updated', 'schema': {'$ref': '#/definitions/Quiz'}}, 404: {}, 500: {} }
    })
    def put(self, quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str)
        parser.add_argument('chapter_id', type=int)
        parser.add_argument('duration_minutes', type=int)
        parser.add_argument('scheduled_date', type=str)
        parser.add_argument('is_active', type=bool)
        data = parser.parse_args()

        if data['title'] is not None: quiz.title = data['title']
        if data['chapter_id'] is not None:
            if not Chapter.query.get(data['chapter_id']): return {'message': f'Chapter with id {data["chapter_id"]} not found'}, 404
            quiz.chapter_id = data['chapter_id']
        if data['duration_minutes'] is not None: quiz.duration_minutes = data['duration_minutes']
        # Handle date parsing for update
        if 'scheduled_date' in data: # Check if key exists, even if None
             quiz.scheduled_date = parse_datetime(data['scheduled_date'])
        if data['is_active'] is not None: quiz.is_active = data['is_active']

        try:
            db.session.commit()
            # Return updated details
            return {
                 'id': quiz.id, 'title': quiz.title, 'chapter_id': quiz.chapter_id,
                 'chapter_name': quiz.chapter.name, 'subject_name': quiz.chapter.subject.name,
                 'duration_minutes': quiz.duration_minutes,
                 'scheduled_date': quiz.scheduled_date.isoformat() if quiz.scheduled_date else None,
                 'is_active': quiz.is_active
            }, 200
        except Exception as e:
            db.session.rollback(); print(f"Error updating quiz: {e}")
            return {'message': f'Error updating quiz'}, 500

    @swag_from({
        'tags': ['Quizzes'], 'summary': 'Delete a quiz',
        'parameters': [{'name': 'quiz_id', 'in': 'path', 'type': 'integer', 'required': True}],
        'responses': { 200: {'description': 'Quiz deleted'}, 404: {}, 500: {} }
    })
    def delete(self, quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        try:
            db.session.delete(quiz)
            db.session.commit()
            return {'message': 'Quiz deleted successfully'}, 200
        except Exception as e:
            db.session.rollback(); print(f"Error deleting quiz: {e}")
            return {'message': f'Error deleting quiz'}, 500

# --- Register Resources ---
api.add_resource(QuizListAPI, '/')
api.add_resource(QuizDetailAPI, '/<int:quiz_id>')
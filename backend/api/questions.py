from flask import Blueprint, jsonify, request # Added jsonify, request
from flask_restful import Api, Resource, reqparse # Added reqparse
from flasgger import swag_from

from core.extensions import db
from core.models import Quiz, Question, Option
from flask_jwt_extended import jwt_required
from .decorators import admin_required_api



# Define the Blueprint
questions_api_bp = Blueprint('questions_api', __name__)
api = Api(questions_api_bp)


class QuizQuestionListAPI(Resource):
    # Apply decorators per method
    @jwt_required() # Any logged-in user can view questions for a quiz
    @swag_from({
        'tags': ['Questions'], 'summary': 'Get questions for a specific quiz',
        'parameters': [{'name': 'quiz_id', 'in': 'path', 'type': 'integer', 'required': True}],
        'responses': { 200: {'description': 'List of questions with options', 'schema': {'$ref': '#/definitions/QuestionListResponse'}}, 404: {} }
    })
    def get(self, quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id, description='Quiz not found')
        questions = Question.query.filter_by(quiz_id=quiz.id).order_by(Question.id).all()
        result = []
        for q in questions:
            options = [{'id': o.id, 'text': o.text, 'is_correct': o.is_correct} for o in q.options.order_by(Option.id).all()]
            result.append({'id': q.id, 'text': q.text, 'quiz_id': q.quiz_id, 'options': options})
        return {'questions': result}

    @jwt_required() # Apply both decorators for admin action
    @jwt_required()
    @admin_required_api
    @swag_from({
        'tags': ['Questions'], 'summary': 'Add a question with options to a specific quiz',
        'parameters': [
            {'name': 'quiz_id', 'in': 'path', 'type': 'integer', 'required': True},
            {'name': 'body', 'in': 'body', 'required': True, 'schema': {'$ref': '#/definitions/QuestionWithOptionsInput'}}
        ],
        'responses': { 201: {'description': 'Question created', 'schema': {'$ref': '#/definitions/QuestionWithOptions'}}, 400: {}, 404: {}, 500: {} }
    })
    def post(self, quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id, description='Quiz not found')
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True, help='Question text cannot be blank')
        parser.add_argument('options', type=list, location='json', required=True, help='Requires a list of 4 option strings')
        parser.add_argument('correct_option_index', type=int, required=True, help='Requires the index (1-4) of the correct option')
        data = parser.parse_args()

        options_list = data['options']
        correct_index = data['correct_option_index']

        if len(options_list) != 4: return {'message': 'Exactly 4 options must be provided'}, 400
        if not (1 <= correct_index <= 4): return {'message': 'correct_option_index must be between 1 and 4'}, 400

        new_question = Question(text=data['text'], quiz_id=quiz.id)
        db.session.add(new_question)
        try:
            db.session.flush()
            created_options = []
            for i, option_text in enumerate(options_list):
                is_correct = (i + 1 == correct_index)
                option = Option(text=option_text, is_correct=is_correct, question_id=new_question.id)
                db.session.add(option)
                created_options.append({'text': option.text, 'is_correct': option.is_correct})

            db.session.commit()
            final_options = [{'id': o.id, 'text': o.text, 'is_correct': o.is_correct} for o in new_question.options.order_by(Option.id).all()]
            return { 'id': new_question.id, 'text': new_question.text, 'quiz_id': new_question.quiz_id, 'options': final_options }, 201
        except Exception as e:
            db.session.rollback(); print(f"Error creating question: {e}")
            return {'message': f'Error creating question/options'}, 500


class QuestionDetailAPI(Resource):
     method_decorators = {
        'get': [jwt_required()], # Any logged-in user can view a question?
        'put': [admin_required_api, jwt_required()],
        'delete': [admin_required_api, jwt_required() ]
    }

     @swag_from({
        'tags': ['Questions'], 'summary': 'Get details of a specific question, including options',
        'parameters': [{'name': 'question_id', 'in': 'path', 'type': 'integer', 'required': True}],
        'responses': { 200: {'description': 'Question details', 'schema': {'$ref': '#/definitions/QuestionWithOptions'}}, 404: {} }
     })
     def get(self, question_id):
         question = Question.query.get_or_404(question_id)
         options = [{'id': o.id, 'text': o.text, 'is_correct': o.is_correct} for o in question.options.order_by(Option.id).all()]
         return {'id': question.id, 'text': question.text, 'quiz_id': question.quiz_id, 'options': options}

     @swag_from({
        'tags': ['Questions'], 'summary': 'Update an existing question and its options',
        'parameters': [
            {'name': 'question_id', 'in': 'path', 'type': 'integer', 'required': True},
            {'name': 'body', 'in': 'body', 'required': True, 'schema': {'$ref': '#/definitions/QuestionWithOptionsInput'}}
        ],
        'responses': { 200: {'description': 'Question updated', 'schema': {'$ref': '#/definitions/QuestionWithOptions'}}, 400: {}, 404: {}, 500: {} }
     })
     def put(self, question_id):
        question = Question.query.get_or_404(question_id)
        options = question.options.order_by(Option.id).all()
        if len(options) != 4: return {'message': 'Question data inconsistent (not 4 options)'}, 500

        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True)
        parser.add_argument('options', type=list, location='json', required=True)
        parser.add_argument('correct_option_index', type=int, required=True)
        data = parser.parse_args()
        options_list = data['options']
        correct_index = data['correct_option_index']

        if len(options_list) != 4: return {'message': 'Exactly 4 options must be provided'}, 400
        if not (1 <= correct_index <= 4): return {'message': 'correct_option_index must be between 1 and 4'}, 400

        try:
            question.text = data['text']
            for i, option_text in enumerate(options_list):
                options[i].text = option_text
                options[i].is_correct = (i + 1 == correct_index)
            db.session.commit()
            final_options = [{'id': o.id, 'text': o.text, 'is_correct': o.is_correct} for o in options]
            return { 'id': question.id, 'text': question.text, 'quiz_id': question.quiz_id, 'options': final_options }, 200
        except Exception as e:
            db.session.rollback(); print(f"Error updating question: {e}")
            return {'message': f'Error updating question/options'}, 500

     @swag_from({
        'tags': ['Questions'], 'summary': 'Delete a question',
        'parameters': [{'name': 'question_id', 'in': 'path', 'type': 'integer', 'required': True}],
        'responses': { 200: {'description': 'Question deleted'}, 404: {}, 500: {} }
     })
     def delete(self, question_id):
        question = Question.query.get_or_404(question_id)
        try:
            db.session.delete(question)
            db.session.commit()
            return {'message': 'Question deleted successfully'}, 200
        except Exception as e:
            db.session.rollback(); print(f"Error deleting question: {e}")
            return {'message': f'Error deleting question'}, 500

# --- Register Resources ---
# Note: These paths are relative to the blueprint prefix defined in app.py ('/api')
api.add_resource(QuizQuestionListAPI, '/quizzes/<int:quiz_id>/questions')
api.add_resource(QuestionDetailAPI, '/questions/<int:question_id>')
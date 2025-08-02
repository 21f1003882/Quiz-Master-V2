# api/admin_api.py
from flask import Blueprint, jsonify
from flask_restful import Api, Resource
from core.extensions import db
from core.models import User, QuizAttempt
from .decorators import admin_required_api
from flask_jwt_extended import jwt_required 

# Define the Blueprint
admin_api_bp = Blueprint('admin_api', __name__)
api = Api(admin_api_bp)

def format_timedelta(td):
    """Helper function to format timedelta objects into a readable string."""
    if not td: return 'N/A'
    minutes, seconds = divmod(td.total_seconds(), 60)
    return f"{int(minutes)}m {int(seconds)}s"

class UserActivityAPI(Resource):
    @jwt_required()
    @admin_required_api
    def get(self, user_id):
        """ Fetches a specific user's details and their full attempt history. """
        user = User.query.get_or_404(user_id)
        
        attempts = QuizAttempt.query.filter_by(user_id=user.id)\
                                    .order_by(QuizAttempt.submitted_at.desc()).all()
        
        attempts_data = [
            {
                'quiz_title': a.quiz.title,
                'chapter_name': a.quiz.chapter.name,
                'subject_name': a.quiz.chapter.subject.name,
                'score': a.score,
                'total_questions': a.total_questions,
                'percentage_score': a.percentage_score,
                'submitted_at': a.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if a.submitted_at else 'Incomplete',
                'time_taken': format_timedelta(a.time_taken)
            } for a in attempts
        ]

        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }

        return jsonify({
            'user': user_data,
            'attempts': attempts_data
        })

api.add_resource(UserActivityAPI, '/users/<int:user_id>/activity')
# api/summary_api.py
from flask import Blueprint, jsonify
from flask_restful import Api, Resource
from core.extensions import db
from core.models import Subject, Chapter, Quiz, Question, User, QuizAttempt
from .decorators import admin_required_api
from sqlalchemy import func
from flask_jwt_extended import jwt_required 

# Define the Blueprint
summary_api_bp = Blueprint('summary_api', __name__)
api = Api(summary_api_bp)

class AdminSummaryAPI(Resource):
    @jwt_required()
    @admin_required_api
   
    def get(self):
        """
        Gathers all data points for the admin summary dashboard.
        """
        try:
            # --- Chart Data ---
            top_scores_query = db.session.query(
                Subject.name,
                func.max(QuizAttempt.score).label('top_score')
            ).join(Chapter, Subject.id == Chapter.subject_id)\
             .join(Quiz, Chapter.id == Quiz.chapter_id)\
             .join(QuizAttempt, Quiz.id == QuizAttempt.quiz_id)\
             .group_by(Subject.name)\
             .order_by(func.max(QuizAttempt.score).desc()).all()

            attempts_query = db.session.query(
                Subject.name,
                func.count(QuizAttempt.id).label('attempt_count')
            ).join(Chapter, Subject.id == Chapter.subject_id)\
             .join(Quiz, Chapter.id == Quiz.chapter_id)\
             .join(QuizAttempt, Quiz.id == QuizAttempt.quiz_id)\
             .group_by(Subject.name)\
             .order_by(func.count(QuizAttempt.id).desc()).all()

            quiz_count_query = db.session.query(
                Subject.name,
                func.count(Quiz.id).label('quiz_count')
            ).join(Chapter, Subject.id == Chapter.subject_id)\
             .join(Quiz, Chapter.id == Quiz.chapter_id)\
             .group_by(Subject.name)\
             .order_by(func.count(Quiz.id).desc()).all()

            chart_data = {
                'top_scores': {'labels': [r.name for r in top_scores_query], 'data': [r.top_score for r in top_scores_query]},
                'attempts': {'labels': [r.name for r in attempts_query], 'data': [r.attempt_count for r in attempts_query]},
                'quiz_count': {'labels': [r.name for r in quiz_count_query], 'data': [r.quiz_count for r in quiz_count_query]}
            }

            # --- Table Data ---
            user_activity_query = db.session.query(
                User.id, User.username, User.email,
                func.count(QuizAttempt.id).label('attempt_count')
            ).outerjoin(QuizAttempt, User.id == QuizAttempt.user_id)\
             .group_by(User.id, User.username, User.email)\
             .order_by(func.count(QuizAttempt.id).desc()).all()
            
            user_activity = [
                {'id': u.id, 'username': u.username, 'email': u.email, 'attempt_count': u.attempt_count}
                for u in user_activity_query
            ]

            quizzes_no_questions_query = db.session.query(Quiz)\
                .outerjoin(Question, Quiz.id == Question.quiz_id)\
                .group_by(Quiz.id)\
                .having(func.count(Question.id) == 0).all()
            
            quizzes_no_questions = [
                {'id': q.id, 'title': q.title, 'chapter_name': q.chapter.name, 'subject_name': q.chapter.subject.name}
                for q in quizzes_no_questions_query
            ]

            # --- Stat Cards Data ---
            content_counts = {
                'users': User.query.count(),
                'subjects': Subject.query.count(),
                'chapters': Chapter.query.count(),
                'quizzes': Quiz.query.count(),
                'questions': Question.query.count()
            }

            return jsonify({
                'chart_data': chart_data,
                'user_activity': user_activity,
                'quizzes_no_questions': quizzes_no_questions,
                'content_counts': content_counts
            })

        except Exception as e:
            print(f"Error in AdminSummaryAPI: {e}")
            return {"message": "An internal error occurred"}, 500

api.add_resource(AdminSummaryAPI, '/')
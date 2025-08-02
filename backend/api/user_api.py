# api/user_api.py
from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
from core.extensions import db, csrf
from core.models import Subject, Chapter, Quiz, Question, Option, QuizAttempt, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime, timezone

user_api_bp = Blueprint('user_api', __name__)
api = Api(user_api_bp)

class UserDashboardDataAPI(Resource):

    @jwt_required()
    def get(self):
        user_identity = get_jwt_identity()
        user = User.query.filter_by(fs_uniquifier=user_identity).first()
        if not user: return {"message": "User not found"}, 404
        user_attempts = QuizAttempt.query.filter_by(user_id=user.id).all()
        high_scores = {}
        for attempt in user_attempts:
            if attempt.quiz_id not in high_scores or attempt.score > high_scores[attempt.quiz_id]['score']:
                high_scores[attempt.quiz_id] = {'score': attempt.score, 'total': attempt.total_questions}
        all_subjects = Subject.query.order_by(Subject.name).all()
        subjects_data = []
        for subject in all_subjects:
            chapters_data = []
            for chapter in subject.chapters.order_by(Chapter.name).all():
                active_quizzes = chapter.quizzes.filter_by(is_active=True).order_by(Quiz.title).all()
                if active_quizzes:
                    chapters_data.append({'id': chapter.id, 'name': chapter.name, 'quizzes': [{'id': q.id, 'title': q.title, 'duration_minutes': q.duration_minutes} for q in active_quizzes]})
            if chapters_data:
                subjects_data.append({'id': subject.id, 'name': subject.name, 'description': subject.description, 'chapters': chapters_data})
        return jsonify({'subjects': subjects_data, 'high_scores': high_scores})

class StartQuizAPI(Resource):
    # ... (This class remains the same as before)
    method_decorators = [csrf.exempt, jwt_required()]
    def post(self, quiz_id):
        user_identity = get_jwt_identity()
        user = User.query.filter_by(fs_uniquifier=user_identity).first()
        quiz = Quiz.query.get_or_404(quiz_id)
        if not quiz.is_active: return {'message': 'This quiz is not currently active.'}, 403
        question_count = quiz.questions.count()
        if question_count == 0: return {'message': 'This quiz has no questions yet. Please check back later.'}, 400
        new_attempt = QuizAttempt(user_id=user.id, quiz_id=quiz.id, score=0, total_questions=question_count)
        db.session.add(new_attempt)
        db.session.commit()
        return jsonify({'attempt_id': new_attempt.id})

class AttendQuizDataAPI(Resource):
    method_decorators = [csrf.exempt, jwt_required()]
    def get(self, attempt_id):
        user_identity = get_jwt_identity()
        user = User.query.filter_by(fs_uniquifier=user_identity).first()
        attempt = QuizAttempt.query.get_or_404(attempt_id)
        if attempt.user_id != user.id: return {'message': 'You are not authorized to view this attempt.'}, 403
        if attempt.submitted_at is not None: return {'message': 'This quiz has already been submitted.'}, 400
        quiz = attempt.quiz
        questions = []
        for q in quiz.questions.order_by(Question.id).all():
            options = [{'id': o.id, 'text': o.text} for o in q.options.order_by(Option.id).all()]
            questions.append({'id': q.id, 'text': q.text, 'options': options})
        time_remaining = None
        if attempt.start_time:
            start_time_utc = attempt.start_time.replace(tzinfo=timezone.utc)
            now_utc = datetime.now(timezone.utc)
            time_elapsed = (now_utc - start_time_utc).total_seconds()
            time_remaining = (quiz.duration_minutes * 60) - time_elapsed
        return jsonify({'attempt_id': attempt.id, 'quiz_title': quiz.title, 'duration_minutes': quiz.duration_minutes, 'time_remaining_seconds': time_remaining, 'questions': questions})
    
    def post(self, attempt_id):
        user_identity = get_jwt_identity()
        user = User.query.filter_by(fs_uniquifier=user_identity).first()
        attempt = QuizAttempt.query.get_or_404(attempt_id)
        if attempt.user_id != user.id: return {'message': 'You are not authorized to submit this attempt.'}, 403
        if attempt.submitted_at is not None: return {'message': 'This quiz has already been submitted.'}, 400
        data = request.get_json()
        user_answers = data.get('answers', {})
        score = 0
        correct_answers = {}
        for question in attempt.quiz.questions:
            correct_option = question.get_correct_option()
            if correct_option:
                correct_answers[question.id] = correct_option.id
                user_option_id = user_answers.get(str(question.id))
                if user_option_id and int(user_option_id) == correct_option.id: score += 1
        attempt.score = score
        attempt.submitted_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({'message': 'Quiz submitted successfully!', 'score': attempt.score, 'total_questions': attempt.total_questions, 'percentage': attempt.percentage_score, 'correct_answers': correct_answers})

class CheckAnswerAPI(Resource):
    method_decorators = [csrf.exempt, jwt_required()]

    def post(self, attempt_id):
        attempt = QuizAttempt.query.get_or_404(attempt_id)
        user_identity = get_jwt_identity()
        user = User.query.filter_by(fs_uniquifier=user_identity).first()

        if attempt.user_id != user.id:
            return {'message': 'Forbidden'}, 403
        if attempt.submitted_at:
            return {'message': 'Attempt already submitted'}, 400

        data = request.get_json()
        question_id = data.get('question_id')
        selected_option_id = data.get('selected_option_id')
        
        if not question_id or not selected_option_id:
            return {'message': 'Missing question or option ID'}, 400

        correct_option = Option.query.filter_by(question_id=question_id, is_correct=True).first()
        if not correct_option:
            return {'message': 'Question configuration error'}, 500

        is_correct = (int(selected_option_id) == correct_option.id)

        return jsonify({
            'correct': is_correct,
            'correct_option_id': correct_option.id
        })

class UserSummaryDataAPI(Resource):
    @jwt_required()
    def get(self):
        user_identity = get_jwt_identity()
        user = User.query.filter_by(fs_uniquifier=user_identity).first()
        if not user:
            return {"message": "User not found"}, 404
        
        # 1. Fetch user's past attempts (no change here)
        attempts = QuizAttempt.query.filter_by(user_id=user.id)\
                                    .join(Quiz)\
                                    .order_by(QuizAttempt.submitted_at.desc()).all()
        
        def format_timedelta(td):
            if not td: return 'N/A'
            minutes, seconds = divmod(td.total_seconds(), 60)
            return f"{int(minutes)}m {int(seconds)}s"

        attempts_data = [
            {
                'quiz_title': a.quiz.title,
                'subject_name': a.quiz.chapter.subject.name,
                'score': a.score,
                'total_questions': a.total_questions,
                'percentage_score': a.percentage_score,
                'submitted_at': a.submitted_at.strftime('%Y-%m-%d %H:%M') if a.submitted_at else 'Incomplete',
                'time_taken': format_timedelta(a.time_taken)
            } for a in attempts
        ]

        
        # Chart 1: Highest Percentage Score per Subject
        # calculate the percentage for each attempt and find the maximum.
        top_scores_query = db.session.query(
            Subject.name,
            func.max(QuizAttempt.score * 100.0 / QuizAttempt.total_questions).label('max_percentage')
        ).select_from(QuizAttempt)\
         .join(Quiz).join(Chapter).join(Subject)\
         .filter(QuizAttempt.user_id == user.id, QuizAttempt.total_questions > 0)\
         .group_by(Subject.name).all()

        # Chart 2: Average Percentage Score per Subject
        # calculate the sum of scores and totals to get an accurate overall average.
        attempts_by_subject_query = db.session.query(
            Subject.name,
            (func.sum(QuizAttempt.score) * 100.0 / func.sum(QuizAttempt.total_questions)).label('avg_percentage')
        ).select_from(QuizAttempt)\
         .join(Quiz).join(Chapter).join(Subject)\
         .filter(QuizAttempt.user_id == user.id, QuizAttempt.total_questions > 0)\
         .group_by(Subject.name).all()
        
        # Format the data for the frontend
        chart_data = {
            'top_scores': {
                'labels': [r.name for r in top_scores_query], 
                'data': [round(r.max_percentage, 1) for r in top_scores_query] # Round to 1 decimal place
            },
            'attempts': {
                'labels': [r.name for r in attempts_by_subject_query], 
                'data': [round(r.avg_percentage, 1) for r in attempts_by_subject_query] # Round to 1 decimal place
            }
        }

        return jsonify({
            'attempts': attempts_data,
            'chart_data': chart_data
        })
api.add_resource(UserDashboardDataAPI, '/dashboard-data')
api.add_resource(StartQuizAPI, '/quizzes/<int:quiz_id>/start')
api.add_resource(AttendQuizDataAPI, '/attempts/<int:attempt_id>')
api.add_resource(CheckAnswerAPI, '/attempts/<int:attempt_id>/check')
api.add_resource(UserSummaryDataAPI, '/summary-data')
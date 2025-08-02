# jobs.py
import os
import csv
import requests
from datetime import datetime, timedelta
from flask import render_template
from flask_mail import Message
from core.extensions import db, mail
from core.models import User, QuizAttempt
from celery_worker import celery

GOOGLE_CHAT_WEBHOOK_URL = os.environ.get('GOOGLE_CHAT_WEBHOOK_URL')

# This function is for APScheduler, so it still needs its own app context.
def send_daily_reminders():
    from app import app
    with app.app_context():
        print("Scheduler: Running daily reminder job...")
        yesterday = datetime.utcnow() - timedelta(days=1)
        active_user_ids_query = db.session.query(QuizAttempt.user_id).filter(QuizAttempt.submitted_at > yesterday).distinct().all()
        active_user_ids = [uid for (uid,) in active_user_ids_query]
        inactive_users = User.query.filter(User.id.notin_(active_user_ids), User.roles.any(name='user')).all()
        if not inactive_users:
            print("Scheduler: All users have been active recently. No reminders to send.")
            return
        # ... (rest of email/chat sending logic is correct) ...

# This is a Celery task. The app context is handled automatically by ContextTask in app.py.
@celery.task
def send_monthly_reports():
    print("Celery: Running monthly report job...")
    today = datetime.utcnow()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
    month_name = first_day_of_previous_month.strftime("%B %Y")
    users = User.query.filter(User.roles.any(name='user')).all()
    
    for user in users:
        attempts = QuizAttempt.query.filter(
            QuizAttempt.user_id == user.id,
            QuizAttempt.submitted_at >= first_day_of_previous_month,
            QuizAttempt.submitted_at <= last_day_of_previous_month
        ).all()

        if not attempts:
            print(f"  - Skipping report for {user.username} (no activity).")
            continue

        total_quizzes_taken = len(attempts)
        total_percentage = sum(a.percentage_score for a in attempts)
        average_score = total_percentage / total_quizzes_taken if total_quizzes_taken > 0 else 0
        html_body = render_template('email/monthly_report.html', username=user.username, month_name=month_name, total_quizzes_taken=total_quizzes_taken, average_score=average_score, attempts=attempts)
        
        try:
            msg = Message(subject=f"Your QuizApp Summary for {month_name}", recipients=[user.email], html=html_body)
            mail.send(msg)
            print(f"  - Monthly report sent to {user.email}")
        except Exception as e:
            print(f"  - FAILED to send monthly report to {user.email}: {e}")

# This is a Celery task. The app context is handled automatically by ContextTask.
@celery.task
def export_user_attempts_csv(user_id):
    from flask import current_app
    app = current_app

    print(f"Celery: Starting CSV export for user_id {user_id}...")
    user = User.query.get(user_id)
    if not user:
        return {'status': 'FAILURE', 'error': 'User not found'}

    export_dir = os.path.join(app.instance_path, 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"user_{user_id}_attempts_{timestamp}.csv"
    filepath = os.path.join(export_dir, filename)
    attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(QuizAttempt.submitted_at.desc()).all()

    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['quiz_id', 'quiz_title', 'chapter_id', 'date_of_quiz', 'score', 'total_questions', 'percentage_score', 'remarks']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for attempt in attempts:
                remarks = "Excellent" if attempt.percentage_score >= 80 else "Good" if attempt.percentage_score >= 50 else "Needs Improvement"
                writer.writerow({
                    'quiz_id': attempt.quiz_id, 'quiz_title': attempt.quiz.title,
                    'chapter_id': attempt.quiz.chapter_id,
                    'date_of_quiz': attempt.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if attempt.submitted_at else 'N/A',
                    'score': attempt.score, 'total_questions': attempt.total_questions,
                    'percentage_score': f"{attempt.percentage_score:.1f}%", 'remarks': remarks
                })
        
        return {'status': 'SUCCESS', 'filename': filename}
    except Exception as e:
        print(f"Celery ERROR: Failed to write CSV for user {user_id}. Error: {e}")
        return {'status': 'FAILURE', 'error': str(e)}
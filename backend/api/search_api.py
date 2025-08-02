from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from core.models import User, Subject, Quiz, Chapter # Import your models
from .decorators import admin_required_api # Assuming you have this decorator
from flask_jwt_extended import jwt_required

# Create a new blueprint for the search API
search_api_bp = Blueprint('search_api', __name__, url_prefix='/api/search')

@search_api_bp.route('/', methods=['GET'])
@jwt_required()
@admin_required_api
def perform_search():
    """
    Searches across users, subjects, and quizzes based on a query parameter 'q'.
    Returns results as a JSON object.
    """
    query_term = request.args.get('q', '').strip()

    if not query_term:
        # Return empty results if no query is provided to avoid unnecessary DB calls
        return jsonify({'users': [], 'subjects': [], 'quizzes': []})
    
    # Use 'ilike' for case-insensitive matching
    search_pattern = f"%{query_term}%"

    # --- Database Queries ---
    
    # Search Users by username or email
    users_found = User.query.filter(
        or_(User.username.ilike(search_pattern), User.email.ilike(search_pattern))
    ).limit(20).all()
    
    # Search Subjects by name or description
    subjects_found = Subject.query.filter(
        or_(Subject.name.ilike(search_pattern), Subject.description.ilike(search_pattern))
    ).limit(20).all()
    
    # Search Quizzes by title, joining to get context
    quizzes_found = Quiz.query.filter(Quiz.title.ilike(search_pattern))\
                              .join(Chapter).join(Subject)\
                              .limit(20).all()

    # --- Serialize Results for JSON Response ---
    
    results = {
        'users': [
            {'id': u.id, 'username': u.username, 'email': u.email} 
            for u in users_found
        ],
        'subjects': [
            {'id': s.id, 'name': s.name, 'description': s.description} 
            for s in subjects_found
        ],
        'quizzes': [
            {
                'id': q.id, 
                'title': q.title, 
                'chapter_name': q.chapter.name, 
                'subject_name': q.chapter.subject.name
            } for q in quizzes_found
        ]
    }

    return jsonify(results)

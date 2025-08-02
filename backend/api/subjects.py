from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource, reqparse
from flasgger import swag_from
from core.extensions import db, cache
from core.models import Subject
from .decorators import admin_required_api
from flask_jwt_extended import jwt_required
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

subjects_api_bp = Blueprint('subjects_api', __name__)
api = Api(subjects_api_bp)

# --- Cache Keys Definition ---
CACHE_KEY_ALL_SUBJECTS = 'all_subjects_list'
CACHE_KEY_SUBJECT_DETAIL_PREFIX = 'subject_detail_' # Will be suffixed with subject_id

class SubjectListAPI(Resource):
    method_decorators = {'get': [jwt_required()], 'post': [admin_required_api, jwt_required()]}

    @swag_from({
        'tags': ['Subjects'], 'summary': 'Get list of subjects',
        'responses': { 200: {'description': 'List of subjects', 'schema': {'$ref': '#/definitions/SubjectListResponse'}}}
    })
    def get(self):
        # Try to get data from cache first
        cached_subjects = cache.get(CACHE_KEY_ALL_SUBJECTS)
        if cached_subjects:
            logger.info("Serving all subjects from cache.")
            return {'subjects': cached_subjects}

        try:
            logger.info("Fetching all subjects from DB.")
            subjects = Subject.query.order_by(Subject.name).all()
            result = [{'id': s.id, 'name': s.name, 'description': s.description} for s in subjects]

            # Store in cache with a suitable timeout (e.g., 5 minutes)
            cache.set(CACHE_KEY_ALL_SUBJECTS, result, timeout=60 * 5)
            return {'subjects': result}
        except Exception as e:
            logger.error(f"Error fetching subjects: {e}")
            return {"message": "Error fetching subjects"}, 500


    @swag_from({
        'tags': ['Subjects'], 'summary': 'Create a new subject',
        'parameters': [{'name': 'body', 'in': 'body', 'required': True, 'schema': {'$ref': '#/definitions/SubjectInput'}}],
        'responses': { 201: {'description': 'Subject created', 'schema': {'$ref': '#/definitions/Subject'}}, 400: {}, 500: {} }
    })
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name is required')
        parser.add_argument('description', type=str, default='')
        data = parser.parse_args()

        if Subject.query.filter_by(name=data['name']).first():
            return {'message': 'Subject name already exists'}, 400

        subject = Subject(name=data['name'], description=data['description'])
        db.session.add(subject)
        try:
            db.session.commit()
            # Invalidate the 'all subjects' cache as the list has changed
            cache.delete(CACHE_KEY_ALL_SUBJECTS)
            logger.info(f"Subject '{subject.name}' created. All subjects cache invalidated.")
            return {'id': subject.id, 'name': subject.name, 'description': subject.description}, 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating subject: {e}")
            return {'message': 'Error creating subject'}, 500

class SubjectDetailAPI(Resource):
     method_decorators = {
        'get': [jwt_required()],
        'put': [admin_required_api, jwt_required()],
        'delete': [admin_required_api, jwt_required()]
    }

     @swag_from({
        'tags': ['Subjects'], 'summary': 'Get details of a specific subject',
        'parameters': [{'name': 'subject_id', 'in': 'path', 'type': 'integer', 'required': True}],
        'responses': { 200: {'description': 'Subject details', 'schema': {'$ref': '#/definitions/Subject'}}, 404: {} }
     })
     def get(self, subject_id):
        cache_key = f'{CACHE_KEY_SUBJECT_DETAIL_PREFIX}{subject_id}'
        cached_subject = cache.get(cache_key)

        if cached_subject:
            logger.info(f"Serving subject {subject_id} from cache.")
            return cached_subject

        subject = Subject.query.get_or_404(subject_id)
        result = {'id': subject.id, 'name': subject.name, 'description': subject.description}

        # Cache the individual subject details for longer (e.g., 30 minutes)
        cache.set(cache_key, result, timeout=60 * 30)
        logger.info(f"Fetching subject {subject_id} from DB and caching.")
        return result
     
     
     @swag_from({
        'tags': ['Subjects'], 'summary': 'Update an existing subject',
        'parameters': [
            {'name': 'subject_id', 'in': 'path', 'type': 'integer', 'required': True},
            {'name': 'body', 'in': 'body', 'required': True, 'schema': {'$ref': '#/definitions/SubjectInputOptional'}}
        ],
        'responses': { 200: {'description': 'Subject updated', 'schema': {'$ref': '#/definitions/Subject'}}, 400: {}, 404: {} }
     })
     def put(self, subject_id):
        subject = Subject.query.get_or_404(subject_id)
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('description', type=str)
        data = parser.parse_args()

        if data['name'] and data['name'] != subject.name:
             if Subject.query.filter(Subject.name == data['name'], Subject.id != subject_id).first():
                 return {'message': 'Another subject with this name already exists'}, 400
             subject.name = data['name']
        if data['description'] is not None:
            subject.description = data['description']
        
        try:
            db.session.commit()
            # Invalidate specific subject detail cache and all subjects list cache
            cache.delete(f'{CACHE_KEY_SUBJECT_DETAIL_PREFIX}{subject_id}')
            cache.delete(CACHE_KEY_ALL_SUBJECTS)
            logger.info(f"Subject {subject_id} updated. Relevant caches invalidated.")
            return {'id': subject.id, 'name': subject.name, 'description': subject.description}, 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating subject: {e}")
            return {'message': 'Error updating subject'}, 500

     @swag_from({
         'tags': ['Subjects'], 'summary': 'Delete a subject',
         'parameters': [{'name': 'subject_id', 'in': 'path', 'type': 'integer', 'required': True}],
         'responses': { 200: {'description': 'Subject deleted'}, 404: {}, 500: {} }
     })
     def delete(self, subject_id):
        subject = Subject.query.get_or_404(subject_id)
        try:
            db.session.delete(subject)
            db.session.commit()
            # Invalidate specific subject detail cache and all subjects list cache
            cache.delete(f'{CACHE_KEY_SUBJECT_DETAIL_PREFIX}{subject_id}')
            cache.delete(CACHE_KEY_ALL_SUBJECTS)
            logger.info(f"Subject {subject_id} deleted. Relevant caches invalidated.")
            return {'message': 'Subject deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting subject: {e}")
            return {'message': 'Error deleting subject'}, 500

# --- Register Resources ---
api.add_resource(SubjectListAPI, '/')
api.add_resource(SubjectDetailAPI, '/<int:subject_id>')
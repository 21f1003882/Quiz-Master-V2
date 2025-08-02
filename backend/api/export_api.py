# api/export_api.py
from flask import Blueprint, jsonify
from flask_restful import Api, Resource
from celery.result import AsyncResult
from core.extensions import csrf
from flask_jwt_extended import jwt_required, get_jwt_identity
from jobs import export_user_attempts_csv 
from core.models import User

export_api_bp = Blueprint('export_api', __name__)
api = Api(export_api_bp)

class UserExportAPI(Resource):
    method_decorators = [csrf.exempt, jwt_required()]

    def post(self):
        """Triggers the CSV export background job for the current user."""
        user_identity = get_jwt_identity()
        user = User.query.filter_by(fs_uniquifier=user_identity).first()
        if not user:
            return {'message': 'User not found'}, 404
        
        # Start the background task and get its ID
        task = export_user_attempts_csv.delay(user.id)
        
        # Immediately return the task ID to the frontend
        return jsonify({'task_id': task.id})

class ExportStatusAPI(Resource):
    method_decorators = [csrf.exempt, jwt_required()]

    def get(self, task_id):
        """Checks the status of a background task."""
        task_result = AsyncResult(task_id)
        
        response = {
            'status': task_result.status,
            'result': None
        }

        if task_result.successful():
            response['result'] = task_result.get() # This will be {'status': 'SUCCESS', 'filename': '...'}
        elif task_result.failed():
            response['result'] = {'status': 'FAILURE', 'error': str(task_result.info)} # Get exception info

        return jsonify(response)

api.add_resource(UserExportAPI, '/user/export-attempts')
api.add_resource(ExportStatusAPI, '/tasks/<string:task_id>/status')
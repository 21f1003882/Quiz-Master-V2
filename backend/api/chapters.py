from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource, reqparse
from flasgger import swag_from
from core.extensions import db
from core.models import Chapter, Subject # Need Subject for checks/joins
from .decorators import admin_required_api
from flask_jwt_extended import jwt_required, current_user as jwt_current_user

# Define the Blueprint
chapters_api_bp = Blueprint('chapters_api', __name__)
api = Api(chapters_api_bp)

definitions = {
    "Chapter": { # Includes subject_name for context in lists
        "type": "object", "properties": {
            "id": {"type": "integer"}, "name": {"type": "string"},
            "subject_id": {"type": "integer"}, "subject_name": {"type": "string"}
        }
    },
     "ChapterInput": { # For POST
        "type": "object", "properties": {
            "name": {"type": "string"}, "subject_id": {"type": "integer"}
        }, "required": ["name", "subject_id"]
    },
    "ChapterInputOptional": { # For PUT
        "type": "object", "properties": { "name": {"type": "string"} }
    },
    "ChapterListResponse": {
         "type": "object", "properties": { "chapters": { "type": "array", "items": {"$ref": "#/definitions/Chapter"} } }
    },
}

class ChapterListAPI(Resource):
    @swag_from({
        'tags': ['Chapters'],
        'summary': 'Get a list of all chapters',
        'parameters': [
             {'name': 'subject_id', 'in': 'query', 'type': 'integer', 'required': False, 'description': 'Filter by subject ID'}
        ],
        'responses': {
            200: {'description': 'A list of chapters', 'schema': {'$ref': '#/definitions/ChapterListResponse'}}
        }
    })
    @jwt_required() 
    def get(self):
        query = Chapter.query
        subject_id = request.args.get('subject_id', type=int)
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        chapters = query.join(Subject).order_by(Subject.name, Chapter.name).all()
        result = [{'id': c.id, 'name': c.name, 'subject_id': c.subject_id, 'subject_name': c.subject.name} for c in chapters]
        return jsonify({'chapters': result})

    @swag_from({
        'tags': ['Chapters'],
        'summary': 'Create a new chapter',
        'parameters': [
            {'name': 'body', 'in': 'body', 'required': True, 'schema': {'$ref': '#/definitions/ChapterInput'}}
        ],
        'responses': {
            201: {'description': 'Chapter created', 'schema': {'$ref': '#/definitions/Chapter'}},
            400: {'description': 'Invalid input or chapter name exists in subject'},
            404: {'description': 'Subject not found'}
        }
    })
    @jwt_required()
    @admin_required_api
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Chapter name cannot be blank')
        parser.add_argument('subject_id', type=int, required=True, help='Subject ID cannot be blank')
        data = parser.parse_args()

        # Check if subject exists
        if not Subject.query.get(data['subject_id']):
            return {'message': f'Subject with id {data["subject_id"]} not found'}, 404

        # Check if chapter name exists within the subject
        if Chapter.query.filter_by(name=data['name'], subject_id=data['subject_id']).first():
            return {'message': f'Chapter "{data["name"]}" already exists in this subject'}, 400

        chapter = Chapter(name=data['name'], subject_id=data['subject_id'])
        db.session.add(chapter)
        try:
            db.session.commit()
            return {'id': chapter.id, 'name': chapter.name, 'subject_id': chapter.subject_id}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error creating chapter: {e}'}, 500


class ChapterDetailAPI(Resource):
    @swag_from({
        'tags': ['Chapters'],
        'summary': 'Get details of a specific chapter',
        'parameters': [{'name': 'chapter_id', 'in': 'path', 'type': 'integer', 'required': True}],
        'responses': {
            200: {'description': 'Chapter details', 'schema': {'$ref': '#/definitions/Chapter'}},
            404: {'description': 'Chapter not found'}
        }
    })
    @jwt_required()
    def get(self, chapter_id):
        chapter = Chapter.query.get_or_404(chapter_id, description='Chapter not found')
        return jsonify({'id': chapter.id, 'name': chapter.name, 'subject_id': chapter.subject_id})

    @swag_from({
        'tags': ['Chapters'],
        'summary': 'Update an existing chapter',
        'parameters': [
            {'name': 'chapter_id', 'in': 'path', 'type': 'integer', 'required': True},
            {'name': 'body', 'in': 'body', 'required': True, 'schema': {'$ref': '#/definitions/ChapterInputOptional'}}
        ],
        'responses': {
             200: {'description': 'Chapter updated', 'schema': {'$ref': '#/definitions/Chapter'}},
             400: {'description': 'Chapter name exists'},
             404: {'description': 'Chapter not found'}
        }
    })
    @jwt_required()
    @admin_required_api
    def put(self, chapter_id):
        chapter = Chapter.query.get_or_404(chapter_id, description='Chapter not found')
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        # Subject ID generally shouldn't be updated via PUT, chapter should be moved via a different mechanism if needed
        data = parser.parse_args()

        if data['name'] and data['name'] != chapter.name:
            if Chapter.query.filter(Chapter.name == data['name'], Chapter.subject_id == chapter.subject_id, Chapter.id != chapter_id).first():
                 return {'message': f'Another chapter named "{data["name"]}" already exists in this subject'}, 400
            chapter.name = data['name']

        try:
            db.session.commit()
            return {'id': chapter.id, 'name': chapter.name, 'subject_id': chapter.subject_id}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error updating chapter: {e}'}, 500


    @swag_from({
        'tags': ['Chapters'],
        'summary': 'Delete a chapter',
        'parameters': [{'name': 'chapter_id', 'in': 'path', 'type': 'integer', 'required': True}],
        'responses': {
            200: {'description': 'Chapter deleted'},
            404: {'description': 'Chapter not found'}
        }
    })
    @jwt_required()
    @admin_required_api
    def delete(self, chapter_id):
        chapter = Chapter.query.get_or_404(chapter_id, description='Chapter not found')
        try:
            db.session.delete(chapter) # Cascade delete handles quizzes etc.
            db.session.commit()
            return {'message': 'Chapter deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error deleting chapter: {e}'}, 500
        
api.add_resource(ChapterListAPI, '/')
api.add_resource(ChapterDetailAPI, '/<int:chapter_id>')

chapters_api_bp.add_app_template_global(definitions, name='chapter_definitions')
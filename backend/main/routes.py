# backend/main/routes.py
from flask import Blueprint, send_from_directory, current_app
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/', defaults={'path': ''})
@main_bp.route('/<path:path>') 
def serve_vue_app(path):
    """Serves the Vue app's index.html for all non-API routes."""
    # static_folder should be set to '../frontend/dist' in app.py
    static_folder = current_app.static_folder

    if static_folder and path != "" and os.path.exists(os.path.join(static_folder, path)):
        # If the path exists in the static folder (e.g., CSS, JS files requested by index.html), serve it.
        return send_from_directory(static_folder, path)
    elif static_folder:
         # Otherwise, serve the index.html shell for Vue Router to handle the path.
         index_path = os.path.join(static_folder, 'index.html')
         if os.path.exists(index_path):
            return send_from_directory(static_folder, 'index.html')
         else:
             return "Frontend index.html not found in static folder.", 404
    else:
        return "Static folder not configured.", 404
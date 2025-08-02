from functools import wraps
from flask_jwt_extended import current_user as jwt_current_user

def admin_required_api(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        print("\n--- [DEBUG] Entering admin_required_api decorator ---")

        # 1. Check if jwt_current_user exists at all
        print(f"[DEBUG] 1. Value of jwt_current_user: {jwt_current_user}")
        print(f"[DEBUG]    Type of jwt_current_user: {type(jwt_current_user)}")

        if not jwt_current_user:
            print("[DEBUG] FAILED: jwt_current_user is None or False.")
            return {'message': 'Admin privileges required (user not found)'}, 403

        # 2. Check if the user object has the 'has_role' method
        has_role_attr = hasattr(jwt_current_user, 'has_role')
        print(f"[DEBUG] 2. Does user have 'has_role' attribute? {has_role_attr}")

        if not has_role_attr:
            print("[DEBUG] FAILED: jwt_current_user object lacks the .has_role method.")
            return {'message': 'Admin privileges required (user object misconfigured)'}, 403

        # 3. If the method exists, try to check the roles
        # Also, print the roles to see what the database is returning
        try:
            user_roles = jwt_current_user.roles
            print(f"[DEBUG] 3a. User roles attribute: {user_roles}")
            # If roles is a list/collection, print each role name
            if hasattr(user_roles, '__iter__'):
                 print(f"[DEBUG] 3b. Role names: {[role.name for role in user_roles]}")
        except Exception as e:
            print(f"[DEBUG] ERROR trying to access user roles: {e}")


        # 4. Perform the final check
        is_admin = jwt_current_user.has_role('admin')
        print(f"[DEBUG] 4. Result of user.has_role('admin'): {is_admin}")

        if not is_admin:
            print("[DEBUG] FAILED: has_role('admin') returned False.")
            print("--- [DEBUG] Exiting decorator ---\n")
            return {'message': 'Admin privileges required'}, 403

        print("[DEBUG] SUCCESS: User is an admin.")
        print("--- [DEBUG] Exiting decorator ---\n")
        return fn(*args, **kwargs)
    return decorated_view
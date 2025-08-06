from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, AuditLog
from app import db

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.is_active:
                return jsonify({'message': 'User not found or inactive'}), 401
            
            if user.role not in allowed_roles:
                return jsonify({'message': 'Insufficient permissions'}), 403
            
            return f(current_user=user, *args, **kwargs)
        return decorated_function
    return decorator

def audit_log(action, resource_type=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            
            try:
                current_user_id = get_jwt_identity()
                if current_user_id:
                    log = AuditLog(
                        user_id=current_user_id,
                        action=action,
                        resource_type=resource_type,
                        ip_address=request.remote_addr,
                        details={'endpoint': request.endpoint, 'method': request.method}
                    )
                    db.session.add(log)
                    db.session.commit()
            except Exception as e:
                # Don't fail the request if audit logging fails
                print(f"Audit logging failed: {e}")
            
            return result
        return decorated_function
    return decorator
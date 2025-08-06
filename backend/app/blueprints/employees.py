from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.models import User
from app.schemas import UserSchema, UserCreateSchema
from app.utils.decorators import role_required, audit_log
from app import db

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('', methods=['GET'])
@role_required('admin', 'manager')
@audit_log('list_employees')
def get_employees(current_user):
    """
    Get all employees
    ---
    tags:
      - Employees
    security:
      - Bearer: []
    responses:
      200:
        description: List of employees
    """
    if current_user.role == 'manager':
        # Managers can only see their direct reports
        employees = User.query.filter_by(manager_id=current_user.id, is_active=True).all()
    else:
        # Admins can see all employees
        employees = User.query.filter_by(is_active=True).all()
    
    schema = UserSchema(many=True)
    return jsonify(schema.dump(employees)), 200

@employees_bp.route('', methods=['POST'])
@role_required('admin')
@audit_log('create_employee', 'user')
def create_employee(current_user):
    """
    Create new employee
    ---
    tags:
      - Employees
    security:
      - Bearer: []
    parameters:
      - in: body
        name: employee
        schema:
          type: object
          required:
            - email
            - password
            - first_name
            - last_name
            - role
    responses:
      201:
        description: Employee created
      400:
        description: Validation error
    """
    try:
        schema = UserCreateSchema()
        data = schema.load(request.json)
        
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400
        
        user = User(**{k: v for k, v in data.items() if k != 'password'})
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        user_schema = UserSchema()
        return jsonify(user_schema.dump(user)), 201
    
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

@employees_bp.route('/<int:employee_id>', methods=['GET'])
@role_required('admin', 'manager', 'employee')
def get_employee(current_user, employee_id):
    """
    Get employee by ID
    ---
    tags:
      - Employees
    security:
      - Bearer: []
    parameters:
      - in: path
        name: employee_id
        type: integer
        required: true
    responses:
      200:
        description: Employee details
      404:
        description: Employee not found
    """
    employee = User.query.get(employee_id)
    
    if not employee or not employee.is_active:
        return jsonify({'message': 'Employee not found'}), 404
    
    # Access control
    if current_user.role == 'employee' and current_user.id != employee_id:
        return jsonify({'message': 'Access denied'}), 403
    elif current_user.role == 'manager' and employee.manager_id != current_user.id and current_user.id != employee_id:
        return jsonify({'message': 'Access denied'}), 403
    
    schema = UserSchema()
    return jsonify(schema.dump(employee)), 200

@employees_bp.route('/<int:employee_id>', methods=['PUT'])
@role_required('admin', 'manager')
@audit_log('update_employee', 'user')
def update_employee(current_user, employee_id):
    """
    Update employee
    ---
    tags:
      - Employees
    security:
      - Bearer: []
    parameters:
      - in: path
        name: employee_id
        type: integer
        required: true
    responses:
      200:
        description: Employee updated
      404:
        description: Employee not found
    """
    employee = User.query.get(employee_id)
    
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404
    
    # Managers can only update their direct reports
    if current_user.role == 'manager' and employee.manager_id != current_user.id:
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        data = request.json
        for key, value in data.items():
            if hasattr(employee, key) and key not in ['id', 'password_hash', 'created_at']:
                setattr(employee, key, value)
        
        db.session.commit()
        
        schema = UserSchema()
        return jsonify(schema.dump(employee)), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Update failed'}), 400

@employees_bp.route('/<int:employee_id>', methods=['DELETE'])
@role_required('admin')
@audit_log('deactivate_employee', 'user')
def deactivate_employee(current_user, employee_id):
    """
    Deactivate employee
    ---
    tags:
      - Employees
    security:
      - Bearer: []
    parameters:
      - in: path
        name: employee_id
        type: integer
        required: true
    responses:
      200:
        description: Employee deactivated
      404:
        description: Employee not found
    """
    employee = User.query.get(employee_id)
    
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404
    
    employee.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Employee deactivated successfully'}), 200
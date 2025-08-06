from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.models import Goal, User
from app.schemas import GoalSchema, GoalCreateSchema
from app.utils.decorators import role_required, audit_log
from app import db

goals_bp = Blueprint('goals', __name__)

@goals_bp.route('', methods=['GET'])
@role_required('admin', 'manager', 'employee')
def get_goals(current_user):
    """
    Get goals based on user role
    ---
    tags:
      - Goals
    security:
      - Bearer: []
    responses:
      200:
        description: List of goals
    """
    if current_user.role == 'admin':
        goals = Goal.query.all()
    elif current_user.role == 'manager':
        # Get goals for direct reports
        direct_reports = User.query.filter_by(manager_id=current_user.id).all()
        employee_ids = [emp.id for emp in direct_reports] + [current_user.id]
        goals = Goal.query.filter(Goal.employee_id.in_(employee_ids)).all()
    else:
        goals = Goal.query.filter_by(employee_id=current_user.id).all()
    
    schema = GoalSchema(many=True)
    return jsonify(schema.dump(goals)), 200

@goals_bp.route('', methods=['POST'])
@role_required('admin', 'manager', 'employee')
@audit_log('create_goal', 'goal')
def create_goal(current_user):
    """
    Create new goal
    ---
    tags:
      - Goals
    security:
      - Bearer: []
    parameters:
      - in: body
        name: goal
        schema:
          type: object
          required:
            - title
    responses:
      201:
        description: Goal created
    """
    try:
        schema = GoalCreateSchema()
        data = schema.load(request.json)
        
        goal = Goal(**data)
        goal.employee_id = current_user.id
        
        db.session.add(goal)
        db.session.commit()
        
        goal_schema = GoalSchema()
        return jsonify(goal_schema.dump(goal)), 201
    
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

@goals_bp.route('/<int:goal_id>', methods=['GET'])
@role_required('admin', 'manager', 'employee')
def get_goal(current_user, goal_id):
    """
    Get goal by ID
    ---
    tags:
      - Goals
    security:
      - Bearer: []
    parameters:
      - in: path
        name: goal_id
        type: integer
        required: true
    responses:
      200:
        description: Goal details
    """
    goal = Goal.query.get(goal_id)
    
    if not goal:
        return jsonify({'message': 'Goal not found'}), 404
    
    # Access control
    if current_user.role == 'employee' and goal.employee_id != current_user.id:
        return jsonify({'message': 'Access denied'}), 403
    elif current_user.role == 'manager':
        employee = User.query.get(goal.employee_id)
        if employee.manager_id != current_user.id and goal.employee_id != current_user.id:
            return jsonify({'message': 'Access denied'}), 403
    
    schema = GoalSchema()
    return jsonify(schema.dump(goal)), 200

@goals_bp.route('/<int:goal_id>', methods=['PUT'])
@role_required('admin', 'manager', 'employee')
@audit_log('update_goal', 'goal')
def update_goal(current_user, goal_id):
    """
    Update goal
    ---
    tags:
      - Goals
    security:
      - Bearer: []
    parameters:
      - in: path
        name: goal_id
        type: integer
        required: true
    responses:
      200:
        description: Goal updated
    """
    goal = Goal.query.get(goal_id)
    
    if not goal:
        return jsonify({'message': 'Goal not found'}), 404
    
    # Access control
    if current_user.role == 'employee' and goal.employee_id != current_user.id:
        return jsonify({'message': 'Access denied'}), 403
    elif current_user.role == 'manager':
        employee = User.query.get(goal.employee_id)
        if employee.manager_id != current_user.id and goal.employee_id != current_user.id:
            return jsonify({'message': 'Access denied'}), 403
    
    try:
        data = request.json
        for key, value in data.items():
            if hasattr(goal, key) and key not in ['id', 'employee_id', 'created_at']:
                setattr(goal, key, value)
        
        db.session.commit()
        
        schema = GoalSchema()
        return jsonify(schema.dump(goal)), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Update failed'}), 400

@goals_bp.route('/<int:goal_id>/approve', methods=['POST'])
@role_required('manager', 'admin')
@audit_log('approve_goal', 'goal')
def approve_goal(current_user, goal_id):
    """
    Approve goal (manager only)
    ---
    tags:
      - Goals
    security:
      - Bearer: []
    parameters:
      - in: path
        name: goal_id
        type: integer
        required: true
    responses:
      200:
        description: Goal approved
    """
    goal = Goal.query.get(goal_id)
    
    if not goal:
        return jsonify({'message': 'Goal not found'}), 404
    
    # Only manager of the employee can approve
    if current_user.role == 'manager':
        employee = User.query.get(goal.employee_id)
        if employee.manager_id != current_user.id:
            return jsonify({'message': 'Access denied'}), 403
    
    goal.manager_approved = True
    goal.status = 'active'
    db.session.commit()
    
    schema = GoalSchema()
    return jsonify(schema.dump(goal)), 200
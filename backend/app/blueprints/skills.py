from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.models import Skill, User
from app.schemas import SkillSchema, SkillCreateSchema
from app.utils.decorators import role_required, audit_log
from app import db

skills_bp = Blueprint('skills', __name__)

@skills_bp.route('', methods=['GET'])
@role_required('admin', 'manager', 'employee')
def get_skills(current_user):
    """
    Get skills based on user role
    ---
    tags:
      - Skills
    security:
      - Bearer: []
    responses:
      200:
        description: List of skills
    """
    if current_user.role == 'admin':
        skills = Skill.query.all()
    elif current_user.role == 'manager':
        # Get skills for direct reports
        direct_reports = User.query.filter_by(manager_id=current_user.id).all()
        employee_ids = [emp.id for emp in direct_reports] + [current_user.id]
        skills = Skill.query.filter(Skill.employee_id.in_(employee_ids)).all()
    else:
        skills = Skill.query.filter_by(employee_id=current_user.id).all()
    
    schema = SkillSchema(many=True)
    return jsonify(schema.dump(skills)), 200

@skills_bp.route('', methods=['POST'])
@role_required('admin', 'manager', 'employee')
@audit_log('create_skill', 'skill')
def create_skill(current_user):
    """
    Create new skill
    ---
    tags:
      - Skills
    security:
      - Bearer: []
    parameters:
      - in: body
        name: skill
        schema:
          type: object
          required:
            - skill_name
    responses:
      201:
        description: Skill created
    """
    try:
        schema = SkillCreateSchema()
        data = schema.load(request.json)
        
        skill = Skill(**data)
        if current_user.role != 'manager' or 'employee_id' not in data:
            skill.employee_id = current_user.id
        
        db.session.add(skill)
        db.session.commit()
        
        skill_schema = SkillSchema()
        return jsonify(skill_schema.dump(skill)), 201
    
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

@skills_bp.route('/<int:skill_id>', methods=['GET'])
@role_required('admin', 'manager', 'employee')
def get_skill(current_user, skill_id):
    """
    Get skill by ID
    ---
    tags:
      - Skills
    security:
      - Bearer: []
    parameters:
      - in: path
        name: skill_id
        type: integer
        required: true
    responses:
      200:
        description: Skill details
    """
    skill = Skill.query.get(skill_id)
    
    if not skill:
        return jsonify({'message': 'Skill not found'}), 404
    
    # Access control
    if current_user.role == 'employee' and skill.employee_id != current_user.id:
        return jsonify({'message': 'Access denied'}), 403
    elif current_user.role == 'manager':
        employee = User.query.get(skill.employee_id)
        if employee.manager_id != current_user.id and skill.employee_id != current_user.id:
            return jsonify({'message': 'Access denied'}), 403
    
    schema = SkillSchema()
    return jsonify(schema.dump(skill)), 200

@skills_bp.route('/<int:skill_id>', methods=['PUT'])
@role_required('admin', 'manager', 'employee')
@audit_log('update_skill', 'skill')
def update_skill(current_user, skill_id):
    """
    Update skill
    ---
    tags:
      - Skills
    security:
      - Bearer: []
    parameters:
      - in: path
        name: skill_id
        type: integer
        required: true
    responses:
      200:
        description: Skill updated
    """
    skill = Skill.query.get(skill_id)
    
    if not skill:
        return jsonify({'message': 'Skill not found'}), 404
    
    # Access control
    if current_user.role == 'employee' and skill.employee_id != current_user.id:
        return jsonify({'message': 'Access denied'}), 403
    elif current_user.role == 'manager':
        employee = User.query.get(skill.employee_id)
        if employee.manager_id != current_user.id and skill.employee_id != current_user.id:
            return jsonify({'message': 'Access denied'}), 403
    
    try:
        data = request.json
        for key, value in data.items():
            if hasattr(skill, key) and key not in ['id', 'employee_id', 'created_at']:
                setattr(skill, key, value)
        
        db.session.commit()
        
        schema = SkillSchema()
        return jsonify(schema.dump(skill)), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Update failed'}), 400
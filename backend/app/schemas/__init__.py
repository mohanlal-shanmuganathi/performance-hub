from marshmallow import Schema, fields, validate, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import User, Goal, Review, Skill

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)
    
    password = fields.Str(load_only=True, validate=validate.Length(min=6))
    full_name = fields.Method('get_full_name')
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class UserCreateSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    role = fields.Str(required=True, validate=validate.OneOf(['admin', 'manager', 'employee']))
    department = fields.Str(validate=validate.Length(max=100))
    position = fields.Str(validate=validate.Length(max=100))
    manager_id = fields.Int()
    hire_date = fields.Date()

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class GoalSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Goal
        load_instance = True
    
    employee_name = fields.Method('get_employee_name')
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"

class GoalCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str()
    category = fields.Str(validate=validate.Length(max=50))
    target_date = fields.Date()
    status = fields.Str(validate=validate.OneOf(['draft', 'active', 'completed', 'cancelled']))
    progress = fields.Int(validate=validate.Range(min=0, max=100))

class ReviewSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Review
        load_instance = True
    
    reviewee_name = fields.Method('get_reviewee_name')
    reviewer_name = fields.Method('get_reviewer_name')
    
    def get_reviewee_name(self, obj):
        return f"{obj.reviewee.first_name} {obj.reviewee.last_name}"
    
    def get_reviewer_name(self, obj):
        return f"{obj.reviewer.first_name} {obj.reviewer.last_name}"

class ReviewCreateSchema(Schema):
    reviewee_id = fields.Int(required=True)
    review_type = fields.Str(required=True, validate=validate.OneOf(['self', 'peer', 'manager']))
    review_period = fields.Str(validate=validate.Length(max=20))
    overall_rating = fields.Int(validate=validate.Range(min=1, max=5))
    technical_skills = fields.Int(validate=validate.Range(min=1, max=5))
    communication = fields.Int(validate=validate.Range(min=1, max=5))
    leadership = fields.Int(validate=validate.Range(min=1, max=5))
    teamwork = fields.Int(validate=validate.Range(min=1, max=5))
    comments = fields.Str()
    strengths = fields.Str()
    areas_for_improvement = fields.Str()

class SkillSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Skill
        load_instance = True

class SkillCreateSchema(Schema):
    skill_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    proficiency_level = fields.Int(validate=validate.Range(min=1, max=5))
    category = fields.Str(validate=validate.Length(max=50))
    target_level = fields.Int(validate=validate.Range(min=1, max=5))
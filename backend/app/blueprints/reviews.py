from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.models import Review, User
from app.schemas import ReviewSchema, ReviewCreateSchema
from app.utils.decorators import role_required, audit_log
from app import db

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('', methods=['GET'])
@role_required('admin', 'manager', 'employee')
def get_reviews(current_user):
    """
    Get reviews based on user role
    ---
    tags:
      - Reviews
    security:
      - Bearer: []
    responses:
      200:
        description: List of reviews
    """
    if current_user.role == 'admin':
        reviews = Review.query.all()
    elif current_user.role == 'manager':
        # Get reviews for direct reports and reviews given by manager
        direct_reports = User.query.filter_by(manager_id=current_user.id).all()
        employee_ids = [emp.id for emp in direct_reports] + [current_user.id]
        reviews = Review.query.filter(
            (Review.reviewee_id.in_(employee_ids)) | 
            (Review.reviewer_id == current_user.id)
        ).all()
    else:
        # Employee can see reviews they've given or received
        reviews = Review.query.filter(
            (Review.reviewee_id == current_user.id) | 
            (Review.reviewer_id == current_user.id)
        ).all()
    
    schema = ReviewSchema(many=True)
    return jsonify(schema.dump(reviews)), 200

@reviews_bp.route('', methods=['POST'])
@role_required('admin', 'manager', 'employee')
@audit_log('create_review', 'review')
def create_review(current_user):
    """
    Create new review
    ---
    tags:
      - Reviews
    security:
      - Bearer: []
    parameters:
      - in: body
        name: review
        schema:
          type: object
          required:
            - reviewee_id
            - review_type
    responses:
      201:
        description: Review created
    """
    try:
        schema = ReviewCreateSchema()
        data = schema.load(request.json)
        
        # Validate review permissions
        reviewee = User.query.get(data['reviewee_id'])
        if not reviewee:
            return jsonify({'message': 'Reviewee not found'}), 404
        
        # Check if user can review this person
        if data['review_type'] == 'manager':
            if current_user.role not in ['manager', 'admin']:
                return jsonify({'message': 'Only managers can give manager reviews'}), 403
            if current_user.role == 'manager' and reviewee.manager_id != current_user.id:
                return jsonify({'message': 'You can only review your direct reports'}), 403
        
        if data['review_type'] == 'self' and data['reviewee_id'] != current_user.id:
            return jsonify({'message': 'You can only create self-reviews for yourself'}), 403
        
        review = Review(**data)
        review.reviewer_id = current_user.id
        
        db.session.add(review)
        db.session.commit()
        
        review_schema = ReviewSchema()
        return jsonify(review_schema.dump(review)), 201
    
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

@reviews_bp.route('/<int:review_id>', methods=['GET'])
@role_required('admin', 'manager', 'employee')
def get_review(current_user, review_id):
    """
    Get review by ID
    ---
    tags:
      - Reviews
    security:
      - Bearer: []
    parameters:
      - in: path
        name: review_id
        type: integer
        required: true
    responses:
      200:
        description: Review details
    """
    review = Review.query.get(review_id)
    
    if not review:
        return jsonify({'message': 'Review not found'}), 404
    
    # Access control
    if current_user.role == 'employee':
        if review.reviewer_id != current_user.id and review.reviewee_id != current_user.id:
            return jsonify({'message': 'Access denied'}), 403
    elif current_user.role == 'manager':
        reviewee = User.query.get(review.reviewee_id)
        if (reviewee.manager_id != current_user.id and 
            review.reviewer_id != current_user.id and 
            review.reviewee_id != current_user.id):
            return jsonify({'message': 'Access denied'}), 403
    
    schema = ReviewSchema()
    return jsonify(schema.dump(review)), 200

@reviews_bp.route('/<int:review_id>', methods=['PUT'])
@role_required('admin', 'manager', 'employee')
@audit_log('update_review', 'review')
def update_review(current_user, review_id):
    """
    Update review
    ---
    tags:
      - Reviews
    security:
      - Bearer: []
    parameters:
      - in: path
        name: review_id
        type: integer
        required: true
    responses:
      200:
        description: Review updated
    """
    review = Review.query.get(review_id)
    
    if not review:
        return jsonify({'message': 'Review not found'}), 404
    
    # Only the reviewer can update their review
    if review.reviewer_id != current_user.id and current_user.role != 'admin':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        data = request.json
        for key, value in data.items():
            if hasattr(review, key) and key not in ['id', 'reviewer_id', 'reviewee_id', 'created_at']:
                setattr(review, key, value)
        
        db.session.commit()
        
        schema = ReviewSchema()
        return jsonify(schema.dump(review)), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Update failed'}), 400

@reviews_bp.route('/<int:review_id>/submit', methods=['POST'])
@role_required('admin', 'manager', 'employee')
@audit_log('submit_review', 'review')
def submit_review(current_user, review_id):
    """
    Submit review
    ---
    tags:
      - Reviews
    security:
      - Bearer: []
    parameters:
      - in: path
        name: review_id
        type: integer
        required: true
    responses:
      200:
        description: Review submitted
    """
    review = Review.query.get(review_id)
    
    if not review:
        return jsonify({'message': 'Review not found'}), 404
    
    if review.reviewer_id != current_user.id and current_user.role != 'admin':
        return jsonify({'message': 'Access denied'}), 403
    
    review.status = 'submitted'
    db.session.commit()
    
    schema = ReviewSchema()
    return jsonify(schema.dump(review)), 200
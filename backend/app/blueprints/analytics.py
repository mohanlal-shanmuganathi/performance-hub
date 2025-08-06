from flask import Blueprint, jsonify
from sqlalchemy import func, and_
from app.models import User, Goal, Review, Skill
from app.utils.decorators import role_required, audit_log
from app import db
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
@role_required('admin', 'manager')
@audit_log('view_dashboard')
def get_dashboard_data(current_user):
    """
    Get dashboard analytics
    ---
    tags:
      - Analytics
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard data
    """
    if current_user.role == 'manager':
        # Manager dashboard - only their team
        direct_reports = User.query.filter_by(manager_id=current_user.id).all()
        employee_ids = [emp.id for emp in direct_reports]
    else:
        # Admin dashboard - all employees
        employee_ids = [user.id for user in User.query.filter_by(is_active=True).all()]
    
    # Goal completion rates
    total_goals = Goal.query.filter(Goal.employee_id.in_(employee_ids)).count()
    completed_goals = Goal.query.filter(
        and_(Goal.employee_id.in_(employee_ids), Goal.status == 'completed')
    ).count()
    
    goal_completion_rate = (completed_goals / total_goals * 100) if total_goals > 0 else 0
    
    # Review completion rates
    total_reviews = Review.query.filter(Review.reviewee_id.in_(employee_ids)).count()
    completed_reviews = Review.query.filter(
        and_(Review.reviewee_id.in_(employee_ids), Review.status == 'completed')
    ).count()
    
    review_completion_rate = (completed_reviews / total_reviews * 100) if total_reviews > 0 else 0
    
    # Average ratings
    avg_ratings = db.session.query(
        func.avg(Review.overall_rating).label('overall'),
        func.avg(Review.technical_skills).label('technical'),
        func.avg(Review.communication).label('communication'),
        func.avg(Review.leadership).label('leadership'),
        func.avg(Review.teamwork).label('teamwork')
    ).filter(
        and_(Review.reviewee_id.in_(employee_ids), Review.overall_rating.isnot(None))
    ).first()
    
    # Department breakdown
    dept_stats = db.session.query(
        User.department,
        func.count(User.id).label('count')
    ).filter(
        and_(User.id.in_(employee_ids), User.department.isnot(None))
    ).group_by(User.department).all()
    
    return jsonify({
        'goal_completion_rate': round(goal_completion_rate, 2),
        'review_completion_rate': round(review_completion_rate, 2),
        'average_ratings': {
            'overall': round(float(avg_ratings.overall or 0), 2),
            'technical': round(float(avg_ratings.technical or 0), 2),
            'communication': round(float(avg_ratings.communication or 0), 2),
            'leadership': round(float(avg_ratings.leadership or 0), 2),
            'teamwork': round(float(avg_ratings.teamwork or 0), 2)
        },
        'department_breakdown': [
            {'department': dept, 'count': count} 
            for dept, count in dept_stats
        ],
        'total_employees': len(employee_ids),
        'total_goals': total_goals,
        'total_reviews': total_reviews
    }), 200

@analytics_bp.route('/performance-trends', methods=['GET'])
@role_required('admin', 'manager')
@audit_log('view_performance_trends')
def get_performance_trends(current_user):
    """
    Get performance trends over time
    ---
    tags:
      - Analytics
    security:
      - Bearer: []
    responses:
      200:
        description: Performance trends data
    """
    if current_user.role == 'manager':
        direct_reports = User.query.filter_by(manager_id=current_user.id).all()
        employee_ids = [emp.id for emp in direct_reports]
    else:
        employee_ids = [user.id for user in User.query.filter_by(is_active=True).all()]
    
    # Get monthly performance data for the last 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Use strftime for SQLite compatibility instead of date_trunc
    monthly_data = db.session.query(
        func.strftime('%Y-%m', Review.created_at).label('month'),
        func.avg(Review.overall_rating).label('avg_rating'),
        func.count(Review.id).label('review_count')
    ).filter(
        and_(
            Review.reviewee_id.in_(employee_ids),
            Review.created_at >= start_date,
            Review.overall_rating.isnot(None)
        )
    ).group_by(
        func.strftime('%Y-%m', Review.created_at)
    ).order_by('month').all()
    
    trends = []
    for month, avg_rating, count in monthly_data:
        trends.append({
            'month': month,  # Already in YYYY-MM format from strftime
            'average_rating': round(float(avg_rating), 2),
            'review_count': count
        })
    
    return jsonify({'trends': trends}), 200

@analytics_bp.route('/team-comparison', methods=['GET'])
@role_required('admin', 'manager')
@audit_log('view_team_comparison')
def get_team_comparison(current_user):
    """
    Get team performance comparison
    ---
    tags:
      - Analytics
    security:
      - Bearer: []
    responses:
      200:
        description: Team comparison data
    """
    if current_user.role == 'manager':
        # For managers, compare their direct reports
        direct_reports = User.query.filter_by(manager_id=current_user.id).all()
        
        team_data = []
        for employee in direct_reports:
            # Get employee's latest review scores
            latest_review = Review.query.filter_by(
                reviewee_id=employee.id
            ).order_by(Review.created_at.desc()).first()
            
            # Get goal completion rate
            total_goals = Goal.query.filter_by(employee_id=employee.id).count()
            completed_goals = Goal.query.filter_by(
                employee_id=employee.id, status='completed'
            ).count()
            
            completion_rate = (completed_goals / total_goals * 100) if total_goals > 0 else 0
            
            team_data.append({
                'employee_name': f"{employee.first_name} {employee.last_name}",
                'department': employee.department,
                'overall_rating': latest_review.overall_rating if latest_review else None,
                'goal_completion_rate': round(completion_rate, 2),
                'total_goals': total_goals
            })
    else:
        # For admins, compare by department
        dept_data = db.session.query(
            User.department,
            func.avg(Review.overall_rating).label('avg_rating'),
            func.count(func.distinct(User.id)).label('employee_count')
        ).join(Review, User.id == Review.reviewee_id)\
         .filter(User.is_active == True)\
         .group_by(User.department).all()
        
        team_data = []
        for dept, avg_rating, emp_count in dept_data:
            if dept:  # Skip null departments
                team_data.append({
                    'department': dept,
                    'average_rating': round(float(avg_rating), 2),
                    'employee_count': emp_count
                })
    
    return jsonify({'team_data': team_data}), 200

@analytics_bp.route('/skills-gap', methods=['GET'])
@role_required('admin', 'manager')
@audit_log('view_skills_gap')
def get_skills_gap_analysis(current_user):
    """
    Get skills gap analysis
    ---
    tags:
      - Analytics
    security:
      - Bearer: []
    responses:
      200:
        description: Skills gap analysis
    """
    if current_user.role == 'manager':
        direct_reports = User.query.filter_by(manager_id=current_user.id).all()
        employee_ids = [emp.id for emp in direct_reports]
    else:
        employee_ids = [user.id for user in User.query.filter_by(is_active=True).all()]
    
    # Get skills with gaps (where current level < target level)
    skills_gaps = db.session.query(
        Skill.skill_name,
        Skill.category,
        func.avg(Skill.proficiency_level).label('avg_current'),
        func.avg(Skill.target_level).label('avg_target'),
        func.count(Skill.id).label('employee_count')
    ).filter(
        and_(
            Skill.employee_id.in_(employee_ids),
            Skill.target_level > Skill.proficiency_level
        )
    ).group_by(Skill.skill_name, Skill.category).all()
    
    gaps_data = []
    for skill, category, avg_current, avg_target, count in skills_gaps:
        gap_size = float(avg_target) - float(avg_current)
        gaps_data.append({
            'skill_name': skill,
            'category': category,
            'average_current_level': round(float(avg_current), 2),
            'average_target_level': round(float(avg_target), 2),
            'gap_size': round(gap_size, 2),
            'employees_affected': count
        })
    
    # Sort by gap size descending
    gaps_data.sort(key=lambda x: x['gap_size'], reverse=True)
    
    return jsonify({'skills_gaps': gaps_data}), 200
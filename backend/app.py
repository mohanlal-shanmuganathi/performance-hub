from app import create_app, db
from app.models import User, Goal, Review, Skill
from datetime import datetime, date
import os
from dotenv import load_dotenv

load_dotenv()

app = create_app()

def seed_data():
    """Seed the database with initial test data"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if data already exists
        if User.query.first():
            print("Database already seeded")
            return
        
        # Create admin user
        admin = User(
            email='admin@company.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            department='IT',
            position='System Administrator',
            hire_date=date(2020, 1, 1),
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create manager
        manager = User(
            email='manager@company.com',
            first_name='John',
            last_name='Manager',
            role='manager',
            department='Engineering',
            position='Engineering Manager',
            hire_date=date(2021, 3, 15),
            is_active=True
        )
        manager.set_password('manager123')
        db.session.add(manager)
        
        # Create employees
        employees = [
            {
                'email': 'employee@company.com',
                'first_name': 'Jane',
                'last_name': 'Employee',
                'department': 'Engineering',
                'position': 'Software Engineer'
            },
            {
                'email': 'alice@company.com',
                'first_name': 'Alice',
                'last_name': 'Smith',
                'department': 'Engineering',
                'position': 'Senior Software Engineer'
            },
            {
                'email': 'bob@company.com',
                'first_name': 'Bob',
                'last_name': 'Johnson',
                'department': 'Marketing',
                'position': 'Marketing Specialist'
            }
        ]
        
        db.session.commit()  # Commit to get manager ID
        
        for emp_data in employees:
            emp = User(
                email=emp_data['email'],
                first_name=emp_data['first_name'],
                last_name=emp_data['last_name'],
                role='employee',
                department=emp_data['department'],
                position=emp_data['position'],
                manager_id=manager.id if emp_data['department'] == 'Engineering' else None,
                hire_date=date(2022, 6, 1),
                is_active=True
            )
            emp.set_password('employee123')
            db.session.add(emp)
        
        db.session.commit()
        
        # Get employee IDs for seeding goals and reviews
        jane = User.query.filter_by(email='employee@company.com').first()
        alice = User.query.filter_by(email='alice@company.com').first()
        
        # Create sample goals
        goals = [
            Goal(
                employee_id=jane.id,
                title='Complete React Training',
                description='Finish advanced React course and build a demo project',
                category='Professional Development',
                target_date=date(2024, 6, 30),
                status='active',
                progress=60,
                manager_approved=True
            ),
            Goal(
                employee_id=alice.id,
                title='Lead Team Project',
                description='Successfully lead the new product feature development',
                category='Leadership',
                target_date=date(2024, 8, 15),
                status='active',
                progress=30,
                manager_approved=True
            )
        ]
        
        for goal in goals:
            db.session.add(goal)
        
        # Create sample reviews
        reviews = [
            Review(
                reviewee_id=jane.id,
                reviewer_id=manager.id,
                review_type='manager',
                review_period='Q1 2024',
                overall_rating=4,
                technical_skills=4,
                communication=3,
                leadership=3,
                teamwork=4,
                comments='Great technical skills, could improve communication',
                strengths='Strong problem-solving abilities',
                areas_for_improvement='Public speaking and presentation skills',
                status='completed'
            ),
            Review(
                reviewee_id=jane.id,
                reviewer_id=jane.id,
                review_type='self',
                review_period='Q1 2024',
                overall_rating=3,
                technical_skills=4,
                communication=3,
                leadership=2,
                teamwork=4,
                comments='I feel confident in my technical abilities but want to work on leadership',
                strengths='Technical problem solving, teamwork',
                areas_for_improvement='Leadership skills, time management',
                status='completed'
            )
        ]
        
        for review in reviews:
            db.session.add(review)
        
        # Create sample skills
        skills = [
            Skill(
                employee_id=jane.id,
                skill_name='Python',
                proficiency_level=4,
                category='Programming',
                target_level=5,
                last_assessed=date.today()
            ),
            Skill(
                employee_id=jane.id,
                skill_name='React',
                proficiency_level=3,
                category='Frontend',
                target_level=4,
                last_assessed=date.today()
            ),
            Skill(
                employee_id=alice.id,
                skill_name='Team Leadership',
                proficiency_level=3,
                category='Soft Skills',
                target_level=4,
                last_assessed=date.today()
            )
        ]
        
        for skill in skills:
            db.session.add(skill)
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
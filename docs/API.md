# API Documentation

## Base URL
- Development: `http://localhost:5000/api`
- Production: `https://your-domain.com/api`

## Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Authentication

#### POST /auth/login
Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "employee",
    "department": "Engineering",
    "position": "Software Engineer"
  }
}
```

#### GET /auth/me
Get current user profile (requires authentication).

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "employee",
  "department": "Engineering",
  "position": "Software Engineer",
  "full_name": "John Doe"
}
```

### Employees

#### GET /employees
Get all employees (Admin/Manager only).

**Response:**
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "employee",
    "department": "Engineering",
    "position": "Software Engineer",
    "manager_id": 2,
    "hire_date": "2022-01-15",
    "is_active": true
  }
]
```

#### POST /employees
Create new employee (Admin only).

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "employee",
  "department": "Marketing",
  "position": "Marketing Specialist",
  "manager_id": 2,
  "hire_date": "2024-01-01"
}
```

#### GET /employees/{id}
Get employee by ID.

#### PUT /employees/{id}
Update employee (Admin/Manager only).

#### DELETE /employees/{id}
Deactivate employee (Admin only).

### Goals

#### GET /goals
Get goals based on user role:
- Admin: All goals
- Manager: Goals for direct reports
- Employee: Own goals only

**Response:**
```json
[
  {
    "id": 1,
    "employee_id": 1,
    "title": "Complete React Training",
    "description": "Finish advanced React course and build demo project",
    "category": "Professional Development",
    "target_date": "2024-06-30",
    "status": "active",
    "progress": 60,
    "manager_approved": true,
    "employee_name": "John Doe",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-15T00:00:00"
  }
]
```

#### POST /goals
Create new goal.

**Request Body:**
```json
{
  "title": "Learn Python",
  "description": "Complete Python fundamentals course",
  "category": "Technical Skills",
  "target_date": "2024-12-31",
  "status": "draft",
  "progress": 0
}
```

#### GET /goals/{id}
Get goal by ID.

#### PUT /goals/{id}
Update goal.

#### POST /goals/{id}/approve
Approve goal (Manager/Admin only).

### Reviews

#### GET /reviews
Get reviews based on user role:
- Admin: All reviews
- Manager: Reviews for direct reports and reviews given by manager
- Employee: Reviews given or received by employee

**Response:**
```json
[
  {
    "id": 1,
    "reviewee_id": 1,
    "reviewer_id": 2,
    "review_type": "manager",
    "review_period": "Q1 2024",
    "overall_rating": 4,
    "technical_skills": 4,
    "communication": 3,
    "leadership": 3,
    "teamwork": 4,
    "comments": "Great technical skills, could improve communication",
    "strengths": "Strong problem-solving abilities",
    "areas_for_improvement": "Public speaking and presentation skills",
    "status": "completed",
    "reviewee_name": "John Doe",
    "reviewer_name": "Jane Manager",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

#### POST /reviews
Create new review.

**Request Body:**
```json
{
  "reviewee_id": 1,
  "review_type": "manager",
  "review_period": "Q2 2024",
  "overall_rating": 4,
  "technical_skills": 4,
  "communication": 3,
  "leadership": 3,
  "teamwork": 4,
  "comments": "Excellent performance this quarter",
  "strengths": "Technical expertise, problem-solving",
  "areas_for_improvement": "Leadership skills"
}
```

#### GET /reviews/{id}
Get review by ID.

#### PUT /reviews/{id}
Update review (only by reviewer).

#### POST /reviews/{id}/submit
Submit review for completion.

### Analytics

#### GET /analytics/dashboard
Get dashboard analytics (Admin/Manager only).

**Response:**
```json
{
  "goal_completion_rate": 75.5,
  "review_completion_rate": 85.2,
  "average_ratings": {
    "overall": 3.8,
    "technical": 4.1,
    "communication": 3.5,
    "leadership": 3.2,
    "teamwork": 4.0
  },
  "department_breakdown": [
    {"department": "Engineering", "count": 15},
    {"department": "Marketing", "count": 8}
  ],
  "total_employees": 23,
  "total_goals": 45,
  "total_reviews": 67
}
```

#### GET /analytics/performance-trends
Get performance trends over time.

**Response:**
```json
{
  "trends": [
    {
      "month": "2024-01",
      "average_rating": 3.8,
      "review_count": 12
    },
    {
      "month": "2024-02",
      "average_rating": 3.9,
      "review_count": 15
    }
  ]
}
```

#### GET /analytics/team-comparison
Get team performance comparison.

**Response:**
```json
{
  "team_data": [
    {
      "employee_name": "John Doe",
      "department": "Engineering",
      "overall_rating": 4,
      "goal_completion_rate": 80.0,
      "total_goals": 5
    }
  ]
}
```

#### GET /analytics/skills-gap
Get skills gap analysis.

**Response:**
```json
{
  "skills_gaps": [
    {
      "skill_name": "Leadership",
      "category": "Soft Skills",
      "average_current_level": 2.5,
      "average_target_level": 4.0,
      "gap_size": 1.5,
      "employees_affected": 8
    }
  ]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "errors": {
    "email": ["Invalid email address"],
    "password": ["Password is required"]
  }
}
```

### 401 Unauthorized
```json
{
  "message": "Invalid credentials"
}
```

### 403 Forbidden
```json
{
  "message": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "message": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "message": "Internal server error"
}
```

## Rate Limiting
- 100 requests per minute per IP address
- 1000 requests per hour per authenticated user

## Pagination
For endpoints that return lists, use query parameters:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

Example: `GET /employees?page=2&per_page=50`

## Interactive API Documentation
Visit `/docs` endpoint for Swagger UI documentation with interactive API testing.
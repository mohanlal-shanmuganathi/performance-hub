# Database Schema

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│      Users      │       │      Goals      │       │     Reviews     │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────┤ employee_id (FK)│       │ id (PK)         │
│ email           │       │ id (PK)         │       │ reviewee_id (FK)│──┐
│ password_hash   │       │ title           │       │ reviewer_id (FK)│──┤
│ first_name      │       │ description     │       │ review_type     │  │
│ last_name       │       │ category        │       │ review_period   │  │
│ role            │       │ target_date     │       │ overall_rating  │  │
│ department      │       │ status          │       │ technical_skills│  │
│ position        │       │ progress        │       │ communication   │  │
│ manager_id (FK) │──┐    │ manager_approved│       │ leadership      │  │
│ hire_date       │  │    │ created_at      │       │ teamwork        │  │
│ is_active       │  │    │ updated_at      │       │ comments        │  │
│ created_at      │  │    └─────────────────┘       │ strengths       │  │
│ updated_at      │  │                              │ areas_for_improv│  │
└─────────────────┘  │                              │ status          │  │
         ▲           │                              │ created_at      │  │
         └───────────┘                              │ updated_at      │  │
                                                    └─────────────────┘  │
                                                             ▲           │
                                                             └───────────┘

┌─────────────────┐       ┌─────────────────┐
│     Skills      │       │   Audit_Logs    │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ employee_id (FK)│──────►│ user_id (FK)    │──────┐
│ skill_name      │       │ action          │      │
│ proficiency_lvl │       │ resource_type   │      │
│ category        │       │ resource_id     │      │
│ last_assessed   │       │ details         │      │
│ target_level    │       │ ip_address      │      │
│ created_at      │       │ timestamp       │      │
└─────────────────┘       └─────────────────┘      │
         ▲                          ▲              │
         └──────────────────────────┼──────────────┘
                                    │
                    ┌───────────────┘
                    │
            ┌─────────────────┐
            │      Users      │
            │   (Reference)   │
            └─────────────────┘
```

## Table Definitions

### Users Table
Stores employee information and authentication data.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role user_roles NOT NULL,
    department VARCHAR(100),
    position VARCHAR(100),
    manager_id INTEGER REFERENCES users(id),
    hire_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TYPE user_roles AS ENUM ('admin', 'manager', 'employee');
```

**Indexes:**
- `idx_users_email` on `email`
- `idx_users_manager_id` on `manager_id`
- `idx_users_role` on `role`
- `idx_users_department` on `department`

### Goals Table
Stores employee goals and progress tracking.

```sql
CREATE TABLE goals (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    target_date DATE,
    status goal_status DEFAULT 'draft',
    progress INTEGER DEFAULT 0,
    manager_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TYPE goal_status AS ENUM ('draft', 'active', 'completed', 'cancelled');
```

**Indexes:**
- `idx_goals_employee_id` on `employee_id`
- `idx_goals_status` on `status`
- `idx_goals_target_date` on `target_date`

**Constraints:**
- `CHECK (progress >= 0 AND progress <= 100)`

### Reviews Table
Stores performance review data for 360-degree feedback.

```sql
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    reviewee_id INTEGER NOT NULL REFERENCES users(id),
    reviewer_id INTEGER NOT NULL REFERENCES users(id),
    review_type review_types NOT NULL,
    review_period VARCHAR(20),
    overall_rating INTEGER,
    technical_skills INTEGER,
    communication INTEGER,
    leadership INTEGER,
    teamwork INTEGER,
    comments TEXT,
    strengths TEXT,
    areas_for_improvement TEXT,
    status review_status DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TYPE review_types AS ENUM ('self', 'peer', 'manager');
CREATE TYPE review_status AS ENUM ('draft', 'submitted', 'completed');
```

**Indexes:**
- `idx_reviews_reviewee_id` on `reviewee_id`
- `idx_reviews_reviewer_id` on `reviewer_id`
- `idx_reviews_type` on `review_type`
- `idx_reviews_period` on `review_period`

**Constraints:**
- `CHECK (overall_rating >= 1 AND overall_rating <= 5)`
- `CHECK (technical_skills >= 1 AND technical_skills <= 5)`
- `CHECK (communication >= 1 AND communication <= 5)`
- `CHECK (leadership >= 1 AND leadership <= 5)`
- `CHECK (teamwork >= 1 AND teamwork <= 5)`
- `UNIQUE (reviewee_id, reviewer_id, review_type, review_period)`

### Skills Table
Tracks employee skills and competency levels.

```sql
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES users(id),
    skill_name VARCHAR(100) NOT NULL,
    proficiency_level INTEGER,
    category VARCHAR(50),
    last_assessed DATE,
    target_level INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_skills_employee_id` on `employee_id`
- `idx_skills_name` on `skill_name`
- `idx_skills_category` on `category`

**Constraints:**
- `CHECK (proficiency_level >= 1 AND proficiency_level <= 5)`
- `CHECK (target_level >= 1 AND target_level <= 5)`
- `UNIQUE (employee_id, skill_name)`

### Audit_Logs Table
Tracks user actions for security and compliance.

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    details JSONB,
    ip_address INET,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_audit_logs_user_id` on `user_id`
- `idx_audit_logs_action` on `action`
- `idx_audit_logs_timestamp` on `timestamp`
- `idx_audit_logs_resource` on `resource_type, resource_id`

## Database Views

### Employee Performance Summary
```sql
CREATE VIEW employee_performance_summary AS
SELECT 
    u.id,
    u.first_name || ' ' || u.last_name AS full_name,
    u.department,
    u.position,
    COUNT(DISTINCT g.id) AS total_goals,
    COUNT(DISTINCT CASE WHEN g.status = 'completed' THEN g.id END) AS completed_goals,
    ROUND(
        COUNT(DISTINCT CASE WHEN g.status = 'completed' THEN g.id END) * 100.0 / 
        NULLIF(COUNT(DISTINCT g.id), 0), 2
    ) AS goal_completion_rate,
    AVG(r.overall_rating) AS avg_overall_rating,
    COUNT(DISTINCT r.id) AS total_reviews
FROM users u
LEFT JOIN goals g ON u.id = g.employee_id
LEFT JOIN reviews r ON u.id = r.reviewee_id AND r.status = 'completed'
WHERE u.is_active = TRUE AND u.role = 'employee'
GROUP BY u.id, u.first_name, u.last_name, u.department, u.position;
```

### Manager Team Overview
```sql
CREATE VIEW manager_team_overview AS
SELECT 
    m.id AS manager_id,
    m.first_name || ' ' || m.last_name AS manager_name,
    COUNT(DISTINCT e.id) AS team_size,
    COUNT(DISTINCT g.id) AS total_team_goals,
    COUNT(DISTINCT CASE WHEN g.status = 'completed' THEN g.id END) AS completed_team_goals,
    AVG(r.overall_rating) AS avg_team_rating
FROM users m
LEFT JOIN users e ON m.id = e.manager_id AND e.is_active = TRUE
LEFT JOIN goals g ON e.id = g.employee_id
LEFT JOIN reviews r ON e.id = r.reviewee_id AND r.status = 'completed'
WHERE m.role = 'manager' AND m.is_active = TRUE
GROUP BY m.id, m.first_name, m.last_name;
```

## Database Functions

### Update Timestamp Trigger
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to tables with updated_at column
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_goals_updated_at BEFORE UPDATE ON goals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reviews_updated_at BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Goal Progress Validation
```sql
CREATE OR REPLACE FUNCTION validate_goal_progress()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.progress = 100 AND NEW.status != 'completed' THEN
        NEW.status = 'completed';
    ELSIF NEW.progress < 100 AND NEW.status = 'completed' THEN
        NEW.status = 'active';
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER validate_goal_progress_trigger BEFORE UPDATE ON goals
    FOR EACH ROW EXECUTE FUNCTION validate_goal_progress();
```

## Data Migration Scripts

### Initial Data Seeding
```sql
-- Insert admin user
INSERT INTO users (email, password_hash, first_name, last_name, role, department, position, hire_date)
VALUES ('admin@company.com', '$2b$12$...', 'Admin', 'User', 'admin', 'IT', 'System Administrator', '2020-01-01');

-- Insert sample departments and positions
INSERT INTO users (email, password_hash, first_name, last_name, role, department, position, manager_id, hire_date)
VALUES 
    ('manager@company.com', '$2b$12$...', 'John', 'Manager', 'manager', 'Engineering', 'Engineering Manager', NULL, '2021-03-15'),
    ('employee@company.com', '$2b$12$...', 'Jane', 'Employee', 'employee', 'Engineering', 'Software Engineer', 2, '2022-06-01');
```

## Performance Optimization

### Recommended Indexes
```sql
-- Composite indexes for common queries
CREATE INDEX idx_reviews_reviewee_period ON reviews(reviewee_id, review_period);
CREATE INDEX idx_goals_employee_status ON goals(employee_id, status);
CREATE INDEX idx_users_department_active ON users(department, is_active);

-- Partial indexes for active records
CREATE INDEX idx_active_users ON users(id) WHERE is_active = TRUE;
CREATE INDEX idx_active_goals ON goals(id) WHERE status IN ('draft', 'active');
```

### Query Optimization Tips
1. Use `EXPLAIN ANALYZE` to identify slow queries
2. Consider partitioning audit_logs table by timestamp
3. Implement connection pooling for high-traffic scenarios
4. Use materialized views for complex analytics queries
5. Regular `VACUUM` and `ANALYZE` operations

## Backup and Recovery

### Backup Strategy
```bash
# Daily full backup
pg_dump -h localhost -U postgres -d performance_db > backup_$(date +%Y%m%d).sql

# Point-in-time recovery setup
# Enable WAL archiving in postgresql.conf:
# wal_level = replica
# archive_mode = on
# archive_command = 'cp %p /path/to/archive/%f'
```

### Recovery Procedures
```bash
# Restore from backup
psql -h localhost -U postgres -d performance_db < backup_20240101.sql

# Point-in-time recovery
pg_basebackup -h localhost -D /path/to/backup -U postgres -v -P -W -R
```
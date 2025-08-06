# Deployment Guide

## Local Development Setup

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Quick Start
1. Clone the repository
2. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
3. Start all services:
   ```bash
   docker-compose up -d
   ```
4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - API Documentation: http://localhost:5000/docs

### Default Login Credentials
- **Admin**: admin@company.com / admin123
- **Manager**: manager@company.com / manager123
- **Employee**: employee@company.com / employee123

## Production Deployment on AWS

### Architecture Overview
```
Internet Gateway
    ↓
Application Load Balancer
    ↓
ECS Fargate Services
    ├── Frontend (React)
    └── Backend (Flask)
    ↓
RDS PostgreSQL Database
```

### AWS Resources Required

#### 1. RDS PostgreSQL Database
```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier performance-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password YourSecurePassword \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --db-subnet-group-name your-db-subnet-group
```

#### 2. ECR Repositories
```bash
# Create ECR repositories
aws ecr create-repository --repository-name performance-backend
aws ecr create-repository --repository-name performance-frontend
```

#### 3. ECS Cluster and Services
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name performance-cluster

# Create task definitions and services (see task-definition.json files)
```

### Environment Variables for Production

#### Backend (.env)
```bash
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/performance_db
SECRET_KEY=your-very-secure-secret-key-change-this
JWT_SECRET_KEY=your-very-secure-jwt-secret-key-change-this
FLASK_ENV=production
```

#### Frontend
```bash
REACT_APP_API_URL=https://your-api-domain.com/api
```

### CI/CD Pipeline

The GitHub Actions workflow automatically:
1. Runs tests on pull requests
2. Builds and pushes Docker images to ECR
3. Updates ECS services with new images
4. Performs zero-downtime deployments

#### Required GitHub Secrets
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### Security Considerations

#### Database Security
- Use RDS with encryption at rest
- Configure security groups to allow access only from ECS tasks
- Use IAM database authentication when possible

#### Application Security
- Use HTTPS/TLS for all communications
- Store secrets in AWS Secrets Manager
- Configure CORS properly for production domains
- Use strong JWT secret keys

#### Network Security
- Deploy in private subnets
- Use Application Load Balancer with SSL termination
- Configure security groups with minimal required access

### Monitoring and Logging

#### CloudWatch Integration
- ECS task logs automatically sent to CloudWatch
- Set up CloudWatch alarms for:
  - High CPU/memory usage
  - Application errors
  - Database connection issues

#### Health Checks
- ALB health checks configured for both services
- Database connection health checks in application

### Scaling Configuration

#### Auto Scaling
```json
{
  "serviceName": "performance-backend-service",
  "minCapacity": 2,
  "maxCapacity": 10,
  "targetCPUUtilization": 70,
  "scaleOutCooldown": 300,
  "scaleInCooldown": 300
}
```

### Backup Strategy

#### Database Backups
- Automated RDS backups with 7-day retention
- Point-in-time recovery enabled
- Cross-region backup replication for disaster recovery

#### Application Data
- Regular database dumps stored in S3
- Configuration and secrets backed up in AWS Secrets Manager

### Cost Optimization

#### Resource Sizing
- **Frontend**: 0.25 vCPU, 512 MB memory
- **Backend**: 0.5 vCPU, 1024 MB memory
- **Database**: db.t3.micro for development, db.t3.small+ for production

#### Cost Monitoring
- Set up AWS Cost Explorer alerts
- Use AWS Budgets for cost control
- Consider Reserved Instances for predictable workloads

### Troubleshooting

#### Common Issues
1. **Database Connection Errors**
   - Check security group rules
   - Verify database credentials
   - Ensure database is in same VPC as ECS tasks

2. **ECS Task Failures**
   - Check CloudWatch logs
   - Verify environment variables
   - Check resource allocation

3. **Load Balancer Health Check Failures**
   - Verify application health endpoints
   - Check security group rules
   - Ensure proper port configuration

#### Useful Commands
```bash
# View ECS service status
aws ecs describe-services --cluster performance-cluster --services performance-backend-service

# View task logs
aws logs get-log-events --log-group-name /ecs/performance-backend --log-stream-name <stream-name>

# Update service with new task definition
aws ecs update-service --cluster performance-cluster --service performance-backend-service --task-definition performance-backend:2
```
# Employee Performance Management System

A production-grade HR performance management system built with React, Flask, and PostgreSQL.

## Architecture Overview

```
├── backend/                 # Flask API server
│   ├── app/
│   │   ├── blueprints/     # Modular API endpoints
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Marshmallow schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities & helpers
│   ├── migrations/         # Alembic migrations
│   ├── tests/             # Backend tests
│   └── requirements.txt
├── frontend/               # React application
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── hooks/         # Custom hooks
│   │   └── utils/         # Utilities
│   └── package.json
├── docker-compose.yml      # Local development setup
└── docs/                  # Documentation
```

## Features

- **Employee Management**: Complete employee lifecycle management
- **Goal Setting**: Quarterly/annual goal tracking with manager approval
- **360° Reviews**: Self, peer, and manager evaluations
- **Skill Assessment**: Competency tracking and development plans
- **Analytics**: Performance dashboards and reporting
- **Security**: JWT authentication with role-based access control

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd AI_Challenge_L2
   ```

2. **Start with Docker**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - API Docs: http://localhost:5000/docs

## Default Login Credentials

- **Admin**: admin@company.com / admin123
- **Manager**: manager@company.com / manager123
- **Employee**: employee@company.com / employee123

## Tech Stack

- **Frontend**: React 18, TailwindCSS, Recharts
- **Backend**: Flask, SQLAlchemy, Marshmallow
- **Database**: PostgreSQL
- **Auth**: JWT with refresh tokens
- **Testing**: Pytest, Jest, Cypress
- **Deployment**: Docker, AWS ECS/EC2 ready

## Environment Variables

See `.env.example` for required environment variables.
# AWS Deployment Guide - Project Status Tracker

This guide covers deploying the Project Status Tracker application to AWS.

## Architecture Overview

### Recommended AWS Services

1. **Backend (FastAPI)**: AWS Elastic Beanstalk or ECS (Fargate)
2. **Frontend (React)**: S3 + CloudFront
3. **Database**: RDS PostgreSQL
4. **File Storage**: S3 (replace local/SharePoint)
5. **Load Balancer**: Application Load Balancer (if using ECS/EC2)
6. **Secrets Management**: AWS Secrets Manager or Parameter Store

## Prerequisites

- AWS Account
- AWS CLI installed and configured
- Docker (for containerized deployment)
- Domain name (optional, for custom domain)

## Option 1: Elastic Beanstalk Deployment (Easiest)

### Step 1: Prepare Backend for Deployment

1. **Create `Procfile` for Elastic Beanstalk:**
```bash
# server/Procfile
web: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. **Create `.ebextensions` configuration:**
```yaml
# server/.ebextensions/01_python.config
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app.main:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
```

3. **Create `requirements.txt` from Poetry:**
```bash
cd server
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### Step 2: Set Up RDS PostgreSQL

1. **Create RDS Instance:**
   - Go to AWS Console → RDS → Create Database
   - Engine: PostgreSQL
   - Template: Free tier (or production)
   - DB instance identifier: `project-status-db`
   - Master username: `postgres`
   - Master password: (set a strong password)
   - VPC: Default or your VPC
   - Public access: Yes (or configure VPC security groups)
   - Security group: Allow inbound on port 5432 from your Beanstalk environment

2. **Note the endpoint:** `project-status-db.xxxxx.us-east-1.rds.amazonaws.com:5432`

### Step 3: Set Up S3 for File Storage

1. **Create S3 Bucket:**
   ```bash
   aws s3 mb s3://project-status-files --region us-east-1
   ```

2. **Configure CORS (if needed):**
   ```json
   [
       {
           "AllowedHeaders": ["*"],
           "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
           "AllowedOrigins": ["*"],
           "ExposeHeaders": []
       }
   ]
   ```

3. **Create IAM Policy for S3 Access:**
   - Create IAM role with S3 read/write permissions
   - Attach to Elastic Beanstalk environment

### Step 4: Deploy Backend to Elastic Beanstalk

1. **Install EB CLI:**
   ```bash
   pip install awsebcli
   ```

2. **Initialize Elastic Beanstalk:**
   ```bash
   cd server
   eb init -p python-3.11 project-status-tracker --region us-east-1
   ```

3. **Create Environment:**
   ```bash
   eb create project-status-env
   ```

4. **Set Environment Variables:**
   ```bash
   eb setenv \
     DATABASE_URL=postgresql://postgres:password@project-status-db.xxxxx.us-east-1.rds.amazonaws.com:5432/projectstatus \
     OPENAI_API_KEY=your-openai-key \
     SECRET_KEY=your-secret-key \
     STORAGE_TYPE=s3 \
     AWS_S3_BUCKET=project-status-files \
     AWS_REGION=us-east-1
   ```

5. **Deploy:**
   ```bash
   eb deploy
   ```

### Step 5: Deploy Frontend to S3 + CloudFront

1. **Build Frontend:**
   ```bash
   cd client
   npm run build
   ```

2. **Create S3 Bucket for Frontend:**
   ```bash
   aws s3 mb s3://project-status-frontend --region us-east-1
   ```

3. **Enable Static Website Hosting:**
   ```bash
   aws s3 website s3://project-status-frontend \
     --index-document index.html \
     --error-document index.html
   ```

4. **Upload Build Files:**
   ```bash
   aws s3 sync client/dist/ s3://project-status-frontend --delete
   ```

5. **Set Up CloudFront Distribution:**
   - Origin: S3 bucket `project-status-frontend`
   - Default root object: `index.html`
   - Error pages: 404 → `/index.html` (for React Router)

6. **Update API URL in Frontend:**
   - Update `VITE_API_URL` in `.env.production` to your Beanstalk URL

## Option 2: ECS (Fargate) Deployment (More Scalable)

### Step 1: Create Docker Images

1. **Backend Dockerfile:**
```dockerfile
# server/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Frontend Dockerfile:**
```dockerfile
# client/Dockerfile
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

3. **Nginx Configuration:**
```nginx
# client/nginx.conf
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### Step 2: Push Images to ECR

```bash
# Create ECR repositories
aws ecr create-repository --repository-name project-status-backend
aws ecr create-repository --repository-name project-status-frontend

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
cd server
docker build -t project-status-backend .
docker tag project-status-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/project-status-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/project-status-backend:latest

# Build and push frontend
cd ../client
docker build -t project-status-frontend .
docker tag project-status-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/project-status-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/project-status-frontend:latest
```

### Step 3: Create ECS Task Definitions

1. **Backend Task Definition** (JSON):
```json
{
  "family": "project-status-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/project-status-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://..."
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:..."
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/project-status-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

2. **Create ECS Cluster and Services:**
   - Create ECS Cluster
   - Create Task Definitions
   - Create Services with Application Load Balancer

## Option 3: EC2 Deployment (Traditional)

### Step 1: Launch EC2 Instance

1. **Launch EC2:**
   - AMI: Ubuntu 22.04 LTS
   - Instance type: t3.medium or larger
   - Security group: Allow HTTP (80), HTTPS (443), SSH (22)

2. **Install Dependencies:**
   ```bash
   sudo apt update
   sudo apt install -y python3.11 python3-pip postgresql-client nginx
   ```

3. **Install Poetry:**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

### Step 2: Set Up Backend

```bash
# Clone repository
git clone <your-repo>
cd project-status-tracker/server

# Install dependencies
poetry install

# Set up environment variables
nano .env
# Add: DATABASE_URL, OPENAI_API_KEY, etc.

# Run migrations
poetry run alembic upgrade head

# Set up systemd service
sudo nano /etc/systemd/system/project-status.service
```

**Systemd Service File:**
```ini
[Unit]
Description=Project Status Tracker API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/project-status-tracker/server
Environment="PATH=/home/ubuntu/.local/bin"
ExecStart=/home/ubuntu/.local/bin/poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable project-status
sudo systemctl start project-status
```

### Step 3: Set Up Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/project-status
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Step 4: Deploy Frontend

```bash
cd client
npm install
npm run build

# Copy to nginx
sudo cp -r dist/* /var/www/html/
```

## Environment Variables for Production

Create a `.env.production` file or use AWS Secrets Manager:

```bash
# Database
DATABASE_URL=postgresql://user:password@rds-endpoint:5432/dbname

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Storage (S3)
STORAGE_TYPE=s3
AWS_S3_BUCKET=project-status-files
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# SharePoint (if using)
SHAREPOINT_SITE_URL=https://yourtenant.sharepoint.com/sites/yoursite
SHAREPOINT_DOCUMENT_LIBRARY=Documents
SHAREPOINT_CLIENT_ID=your-client-id
SHAREPOINT_CLIENT_SECRET=your-client-secret
SHAREPOINT_TENANT_ID=your-tenant-id

# CORS
CORS_ORIGINS=https://your-frontend-domain.com
```

## Database Migration

1. **Connect to RDS:**
   ```bash
   psql -h project-status-db.xxxxx.us-east-1.rds.amazonaws.com -U postgres -d postgres
   ```

2. **Create Database:**
   ```sql
   CREATE DATABASE projectstatus;
   ```

3. **Run Migrations:**
   ```bash
   cd server
   export DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/projectstatus
   poetry run alembic upgrade head
   ```

## Security Considerations

1. **Use AWS Secrets Manager** for sensitive keys
2. **Enable HTTPS** with SSL certificates (AWS Certificate Manager)
3. **Configure Security Groups** to restrict access
4. **Use IAM Roles** instead of access keys where possible
5. **Enable RDS encryption** at rest
6. **Set up VPC** for private networking
7. **Enable CloudWatch Logs** for monitoring

## Monitoring & Logging

1. **CloudWatch Logs:**
   - Application logs
   - Access logs
   - Error tracking

2. **CloudWatch Metrics:**
   - CPU/Memory usage
   - Request counts
   - Error rates

3. **Set Up Alarms:**
   - High error rate
   - High CPU usage
   - Database connection issues

## Cost Estimation (Monthly)

- **RDS PostgreSQL (db.t3.micro)**: ~$15
- **Elastic Beanstalk (t3.small)**: ~$15
- **S3 Storage (10GB)**: ~$0.25
- **CloudFront (10GB transfer)**: ~$1
- **Data Transfer**: ~$5-10

**Total: ~$35-50/month** (for small-scale deployment)

## Quick Start: Elastic Beanstalk (Recommended)

1. **Set up RDS PostgreSQL**
2. **Set up S3 bucket for files**
3. **Deploy backend to Elastic Beanstalk**
4. **Deploy frontend to S3 + CloudFront**
5. **Configure environment variables**
6. **Run database migrations**

## Troubleshooting

- **Database connection issues**: Check security groups and VPC configuration
- **CORS errors**: Update `CORS_ORIGINS` in backend environment
- **File upload issues**: Check S3 bucket permissions and IAM roles
- **Frontend routing issues**: Configure CloudFront error pages

## Next Steps

1. Set up CI/CD pipeline (GitHub Actions + AWS)
2. Configure custom domain with Route 53
3. Set up monitoring and alerts
4. Implement backup strategy for RDS
5. Set up staging environment

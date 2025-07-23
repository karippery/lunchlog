# LunchLog Backend 

## Overview
LunchLog is a Django Rest Framework backend application that allows users to manage their daily lunch receipts and get food recommendations. The system features user authentication, receipt management with image storage (using Minio as an S3-compatible service), restaurant data collection via Google Places API, and recommendation functionality.

## Features

### Core Features
- User authentication (JWT)
- Receipt management with image upload
- Restaurant data collection via Google Places API
- Food recommendations based on location and preferences
- Comprehensive API documentation (Swagger/ReDoc)

### Technical Stack
- Django Rest Framework
- PostgreSQL
- Docker
- Celery with Redis
- Minio (S3-compatible storage)
- Google Places API
- JWT Authentication
- Swagger/ReDoc documentation
- Django Debug Toolbar

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Python 3.x
- Poetry
- Google Places API key (set in environment variables)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd lunchlog
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Copy the environment example file and update with your credentials:
   ```bash
   cp .env.example .env
   ```

4. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

5. Apply migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

6. Create a superuser (optional):
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

### Running the Application

The application will be available at:
- API: `http://localhost:8000/api/`
- Admin: `http://localhost:8000/admin/`
- API Documentation:
  - Swagger: `http://localhost:8000/swagger/`
  - ReDoc: `http://localhost:8000/redoc/`

### Running Tests

To run tests:
```bash
docker-compose exec web pytest
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login (returns JWT tokens)
- `POST /api/v1/auth/token/refresh/` - Refresh JWT token

### Receipts
- `GET /api/v1/receipts/` - List all receipts (paginated)
- `POST /api/v1/receipts/` - Create a new receipt with image upload
- `GET /api/v1/receipts/{id}/` - Retrieve a specific receipt
- `PUT /api/v1/receipts/{id}/` - Update a receipt
- `DELETE /api/v1/receipts/{id}/` - Delete a receipt
- `GET /api/v1/receipts/?month=YYYY-MM` - Filter receipts by month (optional)

### Recommendations
- `GET /api/v1/recommendations/` - Get food recommendations
  - Parameters:
    - `lat` - Latitude
    - `lng` - Longitude
    - `max_distance` - Maximum distance in km (optional)
    - `price_level` - Price level (1-4) (optional)
    - `limit` - Number of results (optional)

## Architecture

The application is divided into three main Django apps:
1. `users` - Handles authentication and user management
2. `receipts` - Manages receipt uploads and storage
3. `restaurants` - Handles restaurant data collection and recommendations

### Scheduled Tasks
- Celery is used to periodically fetch restaurant data from Google Places API
- The task runs daily to update restaurant information


## Deployment (Optional)

For AWS deployment:
1. Set up an ECS cluster with Fargate
2. Configure RDS for PostgreSQL
3. Set up S3 for storage (or use Minio)
4. Configure Elasticache for Redis
5. Update environment variables for production

## Testing

The application includes:
- Unit tests for models and utilities
- API tests for all endpoints
- Integration tests for critical workflows

Run tests with:
```bash
docker-compose exec web pytest
```

## Troubleshooting

- If Minio connection fails, ensure the service is running and credentials are correct
- For Google Places API errors, verify your API key has the necessary permissions
- Check Celery logs for scheduled task issues

## Future Improvements

- Add more recommendation filters (cuisine type, ratings)
- Implement user preferences system
- Add receipt OCR for automatic data extraction
- Enhance error handling and logging

## License

This project is licensed under the MIT License.
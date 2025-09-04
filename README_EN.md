# Green Moment - Smart Carbon Tracking Platform

![Green Moment Logo](assets/leaf_plug_single.png)

## Overview

Green Moment is an innovative mobile application that helps Taiwanese households reduce their carbon footprint by optimizing electricity usage based on real-time carbon intensity data from Taiwan Power Company (Taipower). By shifting energy-intensive activities to low-carbon periods, users can contribute to environmental protection while maintaining their lifestyle.

## Key Features

### 🌱 Real-time Carbon Tracking
- Monitor Taiwan's electricity grid carbon intensity in real-time
- View 24-hour forecasts to plan your activities
- Historical data analysis and trends

### 📱 Smart Appliance Scheduling
- Log household appliance usage
- Get recommendations for optimal usage times
- Track carbon savings from smart scheduling

### 🏆 Gamification & Rewards
- League system based on monthly carbon savings
- Progress from Bronze to Diamond league
- Track your environmental impact

### 🔔 Intelligent Notifications
- Customizable alerts for low-carbon periods
- Personalized recommendations based on your usage patterns
- Daily reminders at your preferred time

### 👤 Flexible Authentication
- Quick start with anonymous mode
- Secure Google Sign-In for data persistence
- Seamless account upgrade from anonymous to registered

## System Architecture

The Green Moment ecosystem consists of three main components:

### 1. Backend API (FastAPI)
- **Location**: `/green_moment_backend_api`
- **Tech Stack**: Python, FastAPI, PostgreSQL, Redis, Firebase
- **Features**:
  - RESTful API with async support
  - JWT-based authentication
  - Real-time data caching
  - Push notification system
  - Automated schedulers for data updates

### 2. Mobile Application (Flutter)
- **Location**: `/green_moment_app`
- **Tech Stack**: Flutter, Dart, Firebase Messaging
- **Platforms**: Android (iOS ready)
- **Features**:
  - Material Design UI
  - Real-time data visualization
  - Offline capability
  - Push notifications

### 3. Data Pipeline
- **Location**: `/green_moment_integrated`
- **Tech Stack**: Python, Pandas
- **Features**:
  - Collects power generation data every 10 minutes
  - Integrates weather data for better predictions
  - Regional carbon intensity calculations

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Flutter 3.8+
- Firebase project with FCM enabled

### Backend Setup

1. **Clone the repository**
```bash
git clone [repository-url]
cd green_moment_backend_api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Setup database**
```bash
# Create database
createdb green_moment

# Run migrations
alembic upgrade head
```

6. **Start services**
```bash
# Terminal 1: API Server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Carbon Data Generator (runs at X9 minutes)
python scripts/carbon_intensity_generator.py --scheduled

# Terminal 3: Notification Scheduler (runs at X0 minutes)
python scripts/run_notification_scheduler.py
```

### Flutter App Setup

1. **Navigate to app directory**
```bash
cd green_moment_app
```

2. **Install dependencies**
```bash
flutter pub get
```

3. **Configure Google Sign-In**
- Add your `google-services.json` to `android/app/`
- Update `android/app/src/main/res/values/strings.xml` with your Web Client ID

4. **Run the app**
```bash
flutter run
```

## Project Structure

```
green_moment/
├── green_moment_backend_api/      # Backend API
│   ├── app/                       # Application code
│   │   ├── api/                   # API endpoints
│   │   ├── core/                  # Core functionality
│   │   ├── models/                # Database models
│   │   ├── schemas/               # Pydantic schemas
│   │   └── services/              # Business logic
│   ├── migrations/                # Database migrations
│   ├── scripts/                   # Utility scripts
│   └── tests/                     # Test suite
│
├── green_moment_app/              # Flutter mobile app
│   ├── lib/                       # Dart source code
│   │   ├── models/                # Data models
│   │   ├── screens/               # UI screens
│   │   ├── services/              # API services
│   │   └── widgets/               # Reusable widgets
│   ├── android/                   # Android configuration
│   └── assets/                    # Images and resources
│
└── green_moment_integrated/       # Data pipeline
    ├── stru_data/                 # Output CSV files
    ├── logs/                      # Log files
    └── config/                    # Configuration
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### Key Endpoints

- **Authentication**
  - `POST /api/v1/auth/google` - Google Sign-In
  - `POST /api/v1/auth/anonymous` - Anonymous login
  
- **Carbon Data**
  - `GET /api/v1/carbon/current` - Current intensity
  - `GET /api/v1/carbon/forecast` - 24-hour forecast
  
- **User Progress**
  - `GET /api/v1/progress/summary` - User statistics
  - `POST /api/v1/chores/log` - Log appliance usage

## Development

### Running Tests
```bash
# Backend tests
cd green_moment_backend_api
pytest

# Flutter tests
cd green_moment_app
flutter test
```

### Code Style
```bash
# Python formatting
black app/
flake8 app/

# Dart formatting
flutter analyze
flutter format lib/
```

## Deployment

### Production Checklist

1. **Security**
   - [ ] Change default database password
   - [ ] Generate secure JWT secret key
   - [ ] Configure HTTPS/SSL
   - [ ] Set up API rate limiting

2. **Configuration**
   - [ ] Update production URLs in Flutter app
   - [ ] Configure Firebase for production
   - [ ] Set up domain and SSL certificates
   - [ ] Configure cloud storage for data files

3. **Infrastructure**
   - [ ] Set up cloud database (Cloud SQL/RDS)
   - [ ] Configure Redis cache
   - [ ] Set up monitoring and logging
   - [ ] Configure auto-scaling

### Deployment Options

**Option 1: Google Cloud Platform**
```yaml
Services:
- Cloud Run: API and schedulers
- Cloud SQL: PostgreSQL
- Memorystore: Redis
- Cloud Storage: Data files
- Cloud Scheduler: Cron jobs
```

**Option 2: Budget-Friendly**
```yaml
Services:
- Render.com: Free tier for API
- Supabase: Free PostgreSQL
- Redis Labs: Free tier
- GitHub Actions: CI/CD
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

- **Documentation**: [Wiki](wiki-url)
- **Issues**: [GitHub Issues](issues-url)
- **Email**: support@greenmoment.tw

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Taiwan Power Company for providing real-time data
- Central Weather Administration for weather data
- All our beta testers and contributors

---

**Green Moment** - Making every watt count for a sustainable future 🌱
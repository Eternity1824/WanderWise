# WanderWise - AI-Powered Travel Planning Platform

WanderWise is an intelligent travel planning platform that uses AI technology to provide users with personalized travel recommendations and route planning. The project consists of two main parts: frontend (React/TypeScript) and backend (FastAPI/Python).

![WanderWise Logo](logo/wanderwise_1.png)

## Features

- 🗺️ Smart itinerary generation and planning
- 🔍 Travel recommendations based on user preferences
- 📍 Interactive map integration (Google Maps API)
- 📝 User notes and favorites functionality
- 🔄 Route optimization
- 🤖 AI-driven travel suggestions

## Tech Stack

### Frontend
- React 19
- TypeScript
- Vite
- Google Maps API

### Backend
- FastAPI
- SQLAlchemy (MySQL)
- Elasticsearch
- OpenAI API

## Installation Guide

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- Docker & Docker Compose
- Google Maps API key

### Clone Repository
```bash
git clone https://github.com/yourusername/WanderWise.git
cd WanderWise
```

## Getting Started

### Backend Setup

1. Start database and Elasticsearch services:
```bash
cd backend
docker-compose up -d
```

2. Install Python dependencies:
```bash
cd fastApiProject
pip install -r app/requirements.txt
```

3. Set up environment variables (create .env file):
```
DATABASE_URL=mysql+pymysql://user:123456@localhost:3306/wanderwise
ELASTICSEARCH_URL=http://localhost:9200
OPENAI_API_KEY=your_openai_api_key
```

4. Run the backend service:
```bash
cd app
uvicorn main:app --reload --port 8082
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure environment variables (create .env.local file):
```
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
VITE_API_BASE_URL=http://localhost:8082
```

3. Start the development server:
```bash
npm run dev
```

4. Access the application:
   Open your browser and navigate to `http://localhost:5173`

## Deployment Guide

### Backend Deployment

1. Deploy backend services and database using Docker Compose:
```bash
cd backend
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

2. Or manually deploy the FastAPI application:
```bash
cd backend/fastApiProject
uvicorn app.main:app --host 0.0.0.0 --port 8082
```

### Frontend Deployment

1. Build the frontend application:
```bash
cd frontend
npm run build
```

2. Deploy the generated `dist` directory to a web server (Nginx, Apache, etc.) or static hosting service (Vercel, Netlify, etc.)


## API Documentation

After starting the backend service, you can access the API documentation at:
- Swagger UI: `http://localhost:8082/docs`
- ReDoc: `http://localhost:8082/redoc`


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Contact

Project Maintainer - [Your Name](mailto:your.email@example.com)

Project Link: [https://github.com/yourusername/WanderWise](https://github.com/yourusername/WanderWise)
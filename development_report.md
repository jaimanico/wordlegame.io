# Wordle Game Application - Development Report

## Table of Contents
1. Introduction
2. SDLC Explanation & Chosen Model
3. Architecture Overview
4. Reflection: Scaling and DevOps Practices
5. AI Usage
6. Conclusion

---

## 1. Introduction

This report overviews my implementation of the Wordle game application developed using tools such as Flask, SQLAlchemy. The application implements a fully functional Wordle clone with RESTful API endpoints, comprehensive data models, and a responsive frontend interface. 

The actual Wordle game is a web-based word puzzle where the user attempts to guess a 5-letter word within 6 attempts. Each guess provides feedback on letter placement and/or presence. The application includes player management, game state tracking, guess validation, and a leaderboard system.

## 2. SDLC Explanation & Chosen Model

### 2.1 SDLC Overview

The Software Development Life Cycle (SDLC) for this Wordle game application followed an **Agile/Iterative model** with elements of DevOps integration. I figures this would be the most optimal since we had a time limit and I still discovered how parts of the code worked while I advanced on others, making it easier to follow on-the-go.

### 2.2 SDLC Phases Applied

**Requirements Analysis:**
- Defined core functionality: player management, game creation, guess submission, feedback display
- Identified data models needed: Player, Game, Guess
- Specified API endpoints for frontend-backend communication
- Planned for scalability and maintainability requirements

**System Design:**
- Architectural design with Flask backend and SQLAlchemy ORM
- RESTful API design with proper endpoints and responses
- Database schema design with relationships between models
- Frontend design with responsive UI elements

**Implementation:**
- Developed backend API endpoints
- Created database models and relationships
- Implemented game logic for Wordle rules
- Built frontend interface for user interaction
- Integrated frontend with backend API calls

**Testing:**
- Unit testing for individual components
- API endpoint testing
- Integration testing between frontend and backend
- User acceptance testing for gameplay functionality

**Deployment:**
- Containerized application using Docker
- Configuration management with environment variables
- CI/CD pipeline setup with GitHub Actions

**Maintenance:**
- Code documentation and comments
- Error handling and logging implementation
- Performance optimization considerations
- Scalability planning

### 2.3 Agile Methodology Benefits

The Agile approach provided several benefits for this project:
- **Iterative Development:** Features were developed incrementally, allowing for continuous testing and feedback
- **Rapid Prototyping:** Quick implementation of core features allowed for early validation
- **Flexibility:** Ability to adapt requirements as development progressed
- **Continuous Integration:** Regular integration of components ensured compatibility
- **Documentation-Driven:** Comprehensive documentation was maintained throughout development

---

## 3. Architecture Overview

### 3.1 High-Level Architecture

The Wordle application follows a three-tier architecture pattern:
```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                   │
│     ┌─────────────────────────────────────────────┐     │
│     │              Frontend UI                    │     │
│     │  HTML, CSS, JavaScript (static files)       │     │
│     └─────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────────┤
│                    Application Layer                    │
│     ┌─────────────────────────────────────────────┐     │
│     │              Flask Backend                  │     │
│     │  API Endpoints, Business Logic, Routing     │     │
│     └─────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────────┤
│                    Data Layer                           │
│     ┌─────────────────────────────────────────────┐     │
│     │           Database (SQLite)                 │     │
│     │         Player, Game, Guess Tables          │     │
│     └─────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Component Architecture

**Frontend Components:**
- `index.html`: Main game interface with player controls and game board
- `style.css`: Styling with responsive design and tile color feedback
- `script.js`: Client-side logic, API communication, and UI updates

**Backend Components:**
- `app.py`: Flask application with API routes and request handling
- `models.py`: SQLAlchemy models for Player, Game, and Guess entities
- `game.py`: Game logic implementation with Wordle rules
- `requirements.txt`: Python dependencies management

**Database Schema:**
- `players` table: Stores player information (id, name, creation date)
- `games` table: Stores game state (id, player_id, target_word, attempts, status)
- `guesses` table: Stores individual guesses (id, game_id, guess, feedback, timestamp)

### 3.3 API Architecture

The application implements a RESTful API, these are the contents.

- `POST /api/players`: Creates a new player
- `POST /api/games`: Starts a new game for a player
- `GET /api/games/{game_id}`: Retrieves game state and history
- `POST /api/games/{game_id}/guess`: Submits a guess for a game
- `GET /api/leaderboard`: Retrieves player statistics and rankings

### 3.4 Data Flow Architecture

```
        Player Input
            │
            ▼
    ┌─────────────────┐
    │ Frontend UI     │
    │ (script.js)     │
    └─────────────────┘
            │ API Calls
            ▼
    ┌─────────────────┐
    │ Flask Backend   │
    │ (app.py)        │
    └─────────────────┘
            │ Database
            ▼
    ┌─────────────────┐
    │ SQLite DB       │
    │ (models.py)     │
    └─────────────────┘
            │ Response
            ▼
    ┌─────────────────┐
    │ Frontend UI     │
    │ (Update View)   │
    └─────────────────┘
```

---

## 4. Reflection: Scaling and DevOps Practices

### 4.1 Current Architecture Strengths


**Containerization:**
- Docker and Docker Compose configurations enable consistent deployment across environments
- Isolated dependencies and environment configuration
- Easy scaling and deployment through container orchestration

**DevOps Integration:**
- GitHub Actions CI pipeline for automated testing
- Automated build and test execution on code changes
- Environment consistency through containerization

**Database Management:**
- SQLAlchemy ORM allows for easy database migrations
- Support for multiple database backends (currently using SQLite)
- Proper data modeling with relationships and constraints

**API Design:**
- RESTful endpoints following standard conventions
- Proper HTTP status codes and error handling
- JSON-based communication protocol

### 4.2 Scaling Options

**Database Scaling:**
- **Migration to PostgreSQL/MySQL**: For production environments, migrate from SQLite to PostgreSQL or MySQL to handle concurrent connections and higher transaction loads
- **Database Connection Pooling**: Implement connection pooling to manage database connections efficiently
- **Read Replicas**: For high-traffic scenarios, implement read replicas for database queries
- **Caching Layer**: Introduce Redis or Memcached for caching frequently accessed data like game states and leaderboards

**Application Scaling:**
- **Horizontal Scaling**: Deploy the application across multiple instances behind a load balancer
- **Microservices Architecture**: Consider breaking the application into smaller services (authentication, game logic, leaderboards)
- **Asynchronous Processing**: Implement background job processing using Celery for game analytics and notifications

**Infrastructure Scaling:**
- **Kubernetes Deployment**: Use Kubernetes for orchestration, auto-scaling, and service discovery
- **CDN Integration**: Use a Content Delivery Network for serving static assets (CSS, JavaScript, images)
- **Monitoring and Logging**: Implement centralized logging with ELK stack and monitoring with Prometheus/Grafana

### 4.3 DevOps Practices Implementation

**CI/CD Pipeline Enhancement:**
- **Automated Testing**: Expand test coverage with integration and end-to-end tests
- **Security Scanning**: Implement SAST and DAST tools for vulnerability detection
- **Automated Deployment**: Set up deployment pipelines for staging and production environments
- **Infrastructure as Code**: Use Terraform or CloudFormation for infrastructure provisioning

**Monitoring and Observability:**
- **Application Performance Monitoring**: Integrate tools like New Relic or DataDog
- **Error Tracking**: Implement error tracking with services like Sentry
- **Log Aggregation**: Centralized logging with structured data for analysis
- **Health Checks**: Implement comprehensive health check endpoints

**Security Practices:**
- **Environment Variables**: Secure handling of sensitive configuration
- **Authentication/Authorization**: Implement user authentication and role-based access control
- **Input Validation**: Comprehensive input validation and sanitization
- **Secure Communication**: HTTPS enforcement and secure headers

### 4.4 Technology Stack Evolution

**Frontend Enhancements:**
- **SPA Framework**: Consider React/Vue.js for more complex frontend functionality
- **State Management**: Implement Redux/Zustand for complex state management
- **Component Library**: Use component libraries for consistent UI patterns

**Backend Enhancements:**
- **API Gateway**: Implement an API gateway for request routing and rate limiting
- **Message Queues**: Use RabbitMQ or Apache Kafka for event-driven architecture
- **API Documentation**: Implement OpenAPI/Swagger for API documentation
- **Rate Limiting**: Add API rate limiting to prevent abuse

**Database Enhancements:**
- **Migration Management**: Implement proper database migration strategies
- **Data Backup**: Regular automated backups with disaster recovery plans
- **Partitioning**: Database partitioning for large-scale data management
- **Performance Tuning**: Query optimization and indexing strategies

### 4.5 Future Architecture Considerations

**Cloud-Native Architecture:**
- **Serverless Functions**: Consider using serverless functions for specific operations like game result processing
- **Event-Driven Architecture**: Implement event sourcing for game state changes
- **API Versioning**: Plan for API versioning for backward compatibility

**Data Analytics:**
- **Game Analytics**: Track user behavior, win rates, and popular words
- **Performance Metrics**: Monitor application performance and user engagement
- **A/B Testing**: Implement A/B testing for UI/UX improvements

---

## 5. AI Usage
For this project, I used AI majorly for the frontend and HTML, since our knowledge in the topic is very limited, this forced me to also twitch some code in the app.py or models.py files, which i also used AI for, since several changes in the frontend could be only fixed with HTML and server/client considerations.
The static/ folder has heavily relied on AI due to foreign languages being used.

---

## 6. Conclusion

This Wordle game works and utilizes containerization, CI/CD, three-tier architecture as well as other tools we-ve discussed in class, the project itself has a lot of up-scaling potential and more implementations in the future.
It also offers an intuitive UI similar to the original game, but with a more minimal approach.
---
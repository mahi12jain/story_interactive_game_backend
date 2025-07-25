# 🎮 Interactive Story Platform - Backend API

A FastAPI-based backend system for creating and playing text-based interactive stories with multiple choice options. Players can navigate through branching storylines by making decisions that affect their journey through the narrative.

## 📖 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [API Endpoints](#-api-endpoints)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage Examples](#-usage-examples)
- [Game Flow](#-game-flow)
- [Contributing](#-contributing)

## ✨ Features

- **User Authentication**: JWT-based authentication with registration and login
- **Story Management**: Create, read, update, and delete interactive stories
- **Dynamic Story Nodes**: Support for different node types (story, choice, ending)
- **Choice System**: Multiple choice options (A, B, C, D) with consequences
- **Game Engine**: Process player choices and navigate story paths
- **Progress Tracking**: Save and resume user progress across sessions
- **Story Validation**: Validate story structure for completeness and logic
- **User Statistics**: Track completed stories, choices made, and playtime
- **Category System**: Organize stories by categories
- **Story Publishing**: Control story visibility with publish/unpublish functionality

## 🛠 Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy (with async support)
- **Authentication**: JWT tokens with passlib
- **Password Hashing**: bcrypt
- **Validation**: Pydantic schemas
- **CORS**: FastAPI CORS middleware

## 📁 Project Structure

```
app/
├── models/                 # SQLAlchemy database models
│   ├── user.py            # User and UserStats models
│   ├── story.py           # Story and StoryNode models
│   ├── choice.py          # Choice model
│   └── user_progress.py   # UserProgress model
├── schemas/               # Pydantic schemas for request/response
│   ├── user_schemas.py
│   ├── story_schemas.py
│   ├── story_nodes_schemas.py
│   ├── choices_schemas.py
│   ├── user_progress_schemas.py
│   ├── user_status_schemas.py
│   └── engine_schemas.py
├── routes/                # API route handlers
│   ├── auth_routes.py
│   ├── story_routes.py
│   ├── story_nodes_routes.py
│   ├── choices_routes.py
│   └── game_engine_routes.py
├── services/              # Business logic services
│   ├── auth_service.py
│   └── game_engine_service.py
├── database.py            # Database configuration
└── main.py               # FastAPI application entry point
```

## 🗄 Database Schema

### Core Entities

#### Users
- `user_id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `password_hash`
- `created_at`, `last_active`

#### Stories
- `story_id` (Primary Key)
- `title`, `description`, `author`
- `difficulty_level`, `category`
- `is_published`, `created_at`

#### Story Nodes
- `node_id` (Primary Key)
- `story_id` (Foreign Key)
- `node_title`, `content`
- `is_starting_node`, `is_ending_node`
- `node_type` (story/choice/ending)

#### Choices
- `choice_id` (Primary Key)
- `from_node_id`, `to_node_id` (Foreign Keys)
- `choice_text`, `choice_letter` (A/B/C/D)
- `consequences` (Optional flavor text)

#### User Progress
- `progress_id` (Primary Key)
- `user_id`, `story_id`, `current_node_id`
- `choice_node` (JSON of choices made)
- `is_completed`, `start_time`, `last_updated`

## 🔌 API Endpoints

### Authentication
```
POST /auth/register          - Register new user
POST /auth/login            - Login user
GET  /auth/me               - Get current user profile
```

### Stories
```
POST   /story/stories            - Create new story
GET    /story/get_story          - Get all stories (paginated)
GET    /story/get_story/{id}     - Get story by ID
PUT    /story/stories/{id}       - Update story
DELETE /story/stories/{id}       - Delete story
GET    /story/stories/categories - Get story categories
```

### Story Nodes
```
POST   /story-nodes/                    - Create story node
GET    /story-nodes/story/{story_id}    - Get all nodes for story
GET    /story-nodes/{node_id}           - Get specific node
PUT    /story-nodes/{node_id}           - Update node
DELETE /story-nodes/{node_id}           - Delete node
GET    /story-nodes/story/{id}/starting-node - Get starting node
```

### Choices
```
POST   /choices/                - Create choice
GET    /choices/node/{node_id}  - Get choices for node
GET    /choices/{choice_id}     - Get specific choice
PUT    /choices/{choice_id}     - Update choice
DELETE /choices/{choice_id}     - Delete choice
GET    /choices/story/{id}/all  - Get all story choices
```

### Game Engine
```
POST /game/start/{story_id}    - Start new story session
POST /game/choice              - Make a choice
GET  /game/current/{story_id}  - Get current progress
GET  /game/validate/{story_id} - Validate story structure
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- PostgreSQL
- pip

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd interactive-story-platform
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart pydantic[email]
```

4. **Set up PostgreSQL database**
```sql
CREATE DATABASE GamingText;
```

5. **Configure environment variables**
Create a `.env` file:
```env
URL_DATABASE=postgresql://postgres:root@localhost:5432/GamingText
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

6. **Run the application**
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## ⚙ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `URL_DATABASE` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 |
| `ALGORITHM` | JWT algorithm | HS256 |

### Database Configuration
The application uses both sync and async database sessions:
- Sync for authentication and migrations
- Async for FastAPI endpoints

## 💡 Usage Examples

### 1. Register and Login
```python
# Register
POST /auth/register
{
    "username": "player1",
    "email": "player1@example.com",
    "password": "securepassword"
}

# Login
POST /auth/login
{
    "username": "player1@example.com",  # email as username
    "password": "securepassword"
}
```

### 2. Create a Story
```python
POST /story/stories
{
    "title": "The Haunted Mansion",
    "description": "A spooky adventure game",
    "author": "StoryTeller",
    "difficulty_level": "medium",
    "category": "horror",
    "is_published": true,
    "created_at": "2024-01-01T00:00:00Z"
}
```

### 3. Create Story Nodes
```python
# Starting node
POST /story-nodes/
{
    "story_id": 1,
    "node_title": "The Entrance",
    "content": "You stand before a dark mansion...",
    "is_starting_node": true,
    "node_type": "story"
}

# Choice node
POST /story-nodes/
{
    "story_id": 1,
    "node_title": "The Decision",
    "content": "You see two paths ahead...",
    "node_type": "choice"
}
```

### 4. Create Choices
```python
POST /choices/
{
    "from_node_id": 1,
    "to_node_id": 2,
    "choice_text": "Enter through the front door",
    "choice_letter": "A",
    "consequences": "You hear creaking sounds..."
}
```

### 5. Play the Game
```python
# Start story
POST /game/start/1

# Make choice
POST /game/choice
{
    "current_node_id": 1,
    "choice_id": 1,
    "user_id": 1
}
```

## 🎮 Game Flow

1. **Story Creation**: Authors create stories with interconnected nodes
2. **Node Types**:
   - **Story nodes**: Narrative content
   - **Choice nodes**: Present options to players
   - **Ending nodes**: Conclude story paths

3. **Player Journey**:
   - Start at the beginning node
   - Read content and make choices
   - Progress through story based on decisions
   - Reach different endings based on choices made

4. **Progress Tracking**: Save player position and choice history
5. **Statistics**: Track completion rates and user engagement

## 🏗 Story Structure Validation

The system validates stories for:
- ✅ Single starting node
- ✅ At least one ending node
- ✅ No unreachable nodes
- ✅ No dead ends (except endings)
- ✅ No choice letter conflicts
- ✅ Valid node connections

## 🔐 Authentication Flow

1. User registers with email/username/password
2. Password is hashed using bcrypt
3. Login returns JWT access token
4. Token required for protected endpoints
5. Token contains user ID for session management

## 📊 User Statistics

Track user engagement with:
- Stories completed
- Total choices made
- Favorite categories
- Total playtime
- Progress across multiple stories

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔧 Development Notes

- Database tables are auto-created on startup
- CORS is enabled for all origins (configure for production)
- JWT tokens expire after 30 minutes by default
- All passwords are hashed using bcrypt
- Async endpoints for better performance

## 📞 Support

For questions or issues, please create an issue in the repository or contact the development team.

---

**Happy storytelling! 🎭📚**

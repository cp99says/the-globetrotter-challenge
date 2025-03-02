## Game Application - README

### Overview
Welcome to the Game Application, an interactive platform where users can participate in exciting quizzes and trivia games. The application seamlessly manages game sessions, tracks user scores, and ensures smooth interaction between players and the game server.


---

## Architecture

The application follows a monolithic architecture and is built with a structured approach, including the following key components:

- **Database Schema**: Uses PostgreSQL for secure and structured data storage.
- **API Flow**: The backend exposes a RESTful API to handle game logic and user interactions.
- **Low-Level Design (LLD)**: A detailed class diagram illustrates the interaction between various components, such as game managers and session handlers.
- **Data Flow Diagram (DFD)**: Represents how data moves through the system, showing different data sources and interactions.

---

## Features
- Game Creation & Management
- Real-time Question Fetching
- Answer Validation & Scoring
- Leaderboard Tracking
- Game Session Management

---

# Getting Started

## Prerequisites

Ensure you have the following installed before running the application:

- Python 3.x
- Django
- PostgreSQL
- Django REST Framework

## Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/game-app.git
cd game-app

# Install dependencies
pip install -r requirements.txt

# Set up the database
python manage.py migrate

# Start the server
python manage.py runserver
```

## **System Design Components**

### **1. Database Schema**
The application consists of multiple tables, including:

- `Game` - Stores details about each game session.
- `GameSession` - Tracks user participation and progress.
- `GameAttempts` - Stores user responses to quiz questions.
- `Leaderboard` - Maintains rankings and scores.
- `Questionnaire` - Holds trivia questions and their metadata.
- `User` - Stores user details and authentication data.

**Schema Diagram:**
![Database Schema](db%20schema.png)

---

### **2. API Flow**
The API follows a structured flow where:

1. The user starts a game via `StartGameView`.
2. The game session is created and assigned to the user.
3. Questions are fetched dynamically via `NextQuestionView`.
4. Users submit answers via `AnswerSubmissionView`, where validation occurs.
5. Scores and game statistics are updated and fetched as needed.
6. The game ends via `EndGameSessionView`, returning a summary to the user.

**API Flow Diagram:**
![API Flow](API%20flow.png)

---

### **3. Sequence Diagram**
The sequence diagram demonstrates the step-by-step interaction between the user, API endpoints, and the database. It includes processes like game initialization, answer submission, result calculation, and session termination.
![Sequence Flow](sequence%20diagram.png)
---

### **4. Data Flow Diagram (DFD)**
The DFD illustrates the data movement in the application, showcasing how input data (such as user responses) flows through various processing stages before producing results (such as updated leaderboards).

**DFD Image:**
![Data Flow Diagram](data%20flow%20diagram.png)

# API Endpoints

## Start a Game 🎮

**POST** `/start-game/`

### Response:
```json
{
  "game_id": "12345",
  "session_id": "67890",
  "user_id": "abcde",
  "question": ["Clue 1", "Clue 2"],
  "options": ["Paris", "London", "Berlin"]
}
```
### Submit an Answer ✅
**POST** `/submit-answer/`
### Request:
```json
{
    "game_id": "019552ca-29e9-7a59-8219-cc469eef6250",
    "session_id": "019552ca-29f5-7af2-9a4c-c8a0e9f2eee9",
    "questionnaire_id": "01955020-dba7-7aad-8b35-3d7a3200e220",
    "user_id": "019552ca-29f4-7030-904c-24c62c9cb8c6",
    "response": "Paris"
}
```
### Response:
```json
{
  "message": "Oopsie! \ud83d\ude48 That\u2019s not it. But hey, nobody\u2019s perfect!", 
  "attempt_number": 2
}
```
### End Game Session 🏁

**POST** `/api/end-session/`

### Request:
```json
{
    "session_id": "019550fb-67ad-7824-a219-3ff83907f686"
}
```
### Response:
```json
{
    "message": "Session ended successfully",
    "correct_submissions": 1,
    "total_attempts": 2
}
```

### Generate Invite Link 🔗

**POST** `/api/invite-link/`

### Request:
```json
{
    "username": "cp99says",
    "game_id": "019552ca-29e9-7a59-8219-cc469eef6250",
    "session_id": "019552ca-29f5-7af2-9a4c-c8a0e9f2eee9",
    "user_id": "019552ca-29f4-7030-904c-24c62c9cb8c6"
}
```
### Response:
```json
{
    "invite-link": "https://demo-game.com/xhdeyu9"
}
```

### Join Session Invite Link 🔗

**POST** `/api/join-session/`

### Request:
```json
{
    "invite_code": "plGCJJ3",
    "username": "cp99says2"
}
```
### Response:
```json
{
    "message": "You've successfully joined the session! Let's play!"
}
```


### View friend score

**GET** `/api/view-friend-score/?username=test123`


### Response:
```json
{
    "invitor": "cp99says",
    "correct_answers": 3,
    "incorrect_answers": 6,
    "total_attempts": 9
}
```


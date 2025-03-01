Game Application - README

Overview

This project is a monolithic game application that enables users to participate in interactive quizzes and trivia games. The system manages game sessions, tracks user scores, and facilitates seamless interaction between players and the game server.

Architecture

The application follows a monolithic architecture and is built with a structured approach, including the following key components:

Database Schema: PostgreSQL is used for storing game data, user sessions, and attempts.

API Flow: The backend exposes a RESTful API to handle game logic and user interactions.

Low-Level Design (LLD): A detailed class diagram illustrates the interaction between various components, such as game managers and session handlers.

Data Flow Diagram (DFD): Represents how data moves through the system, showing different data sources and interactions.

Features

User Authentication (if applicable)

Game Creation & Management

Real-time Question Fetching

Answer Validation & Scoring

Leaderboard Tracking

Game Session Management

System Design Components

1. Database Schema

The application consists of multiple tables, including:

Game - Stores details about each game session.

GameSession - Tracks user participation and progress.

GameAttempts - Stores user responses to quiz questions.

Leaderboard - Maintains rankings and scores.

Questionnaire - Holds trivia questions and their metadata.

User - Stores user details and authentication data.

2. API Flow

The API follows a structured flow where:

The user starts a game via StartGameView.

The game session is created and assigned to the user.

Questions are fetched dynamically via NextQuestionView.

Users submit answers via AnswerSubmissionView, where validation occurs.

Scores and game statistics are updated and fetched as needed.

The game ends via EndGameSessionView, returning a summary to the user.

3. Sequence Diagram

The sequence diagram demonstrates the step-by-step interaction between the user, API endpoints, and the database. It includes processes like game initialization, answer submission, result calculation, and session termination.

4. Data Flow Diagram (DFD)

The DFD illustrates the data movement in the application, showcasing how input data (such as user responses) flows through various processing stages before producing results (such as updated leaderboards).

Setup Instructions

To set up and run the application locally:

Clone the repository:

git clone <repository-url>

Navigate to the project directory:

cd game-application

Install dependencies:

pip install -r requirements.txt

Set up the database:

python manage.py migrate

Run the server:

python manage.py runserver

Access the API via http://localhost:8000/api/

Future Improvements

Implement real-time multiplayer mode.

Add a microservices architecture for better scalability.

Integrate third-party authentication.

Implement caching mechanisms to optimize performance.

Contributing

If you would like to contribute, please fork the repository and submit a pull request with detailed descriptions of your changes.

License

This project is licensed under the MIT License. See LICENSE for more details.

Additional Notes

The attached diagrams provide a detailed visualization of the system, helping developers understand how the application components interact. Be sure to refer to them while working on the project.


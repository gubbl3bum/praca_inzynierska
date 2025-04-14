
---

### README for the Entire Application (`README.md`)

```md
# WolfRead Application

WolfRead is a platform for book enthusiasts to discover, review, and organize their favorite books. It consists of a React-based frontend and a Django-based backend.

## Prerequisites

- Docker and Docker Compose (recommended for running the entire application)
- Alternatively:
  - Node.js and npm for the frontend
  - Python 3.9+ and PostgreSQL for the backend

## Running the Application with Docker Compose

1. Ensure Docker and Docker Compose are installed on your system.

2. Navigate to the root directory of the project:
   ```bash

3. Start the application:
    ```bash
    docker-compose up --build

4. Access the application

- frontend: http://localhost:3000
- backend API: http://localhost:8000/api/

## Notes

- The frontend and backend communicate via API endpoints. Ensure both are running for full functionality.

- Use Docker Compose for a seamless setup of the entire application.


uruchomienie django:
python -m django startproject config .
cd frontend
npm install
cd ..

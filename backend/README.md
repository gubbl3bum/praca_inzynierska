# WolfRead Backend

This is the backend of the WolfRead application, built with Django and Django REST Framework.

## Prerequisites

- Python 3.9 or higher
- PostgreSQL
- pip (Python package manager)

## Installation

1. Navigate to the `backend` directory:
   ```bash
   cd backend

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate

3. Install the dependencies
    ```bash
    pip install -r requirements.txt

4. Set up the database:

- Ensure PostgreSQL is running

- Create a database named `database_name` with the user `*username*` and password `*password*` // TODO: Update this

5. Apply migration
    ```bash
    python manage.py migrate

## Running the Application

1. Start the development server:
    ```bash
    python manage.py runserver

2. The backend will be avaliable at http://localhost:8000

## Running with Docker

1. Build the Docker image:
    ```bash
    docker build -t wolfread-backend .

2. Run the container
    ```bash
    docker run -p 8000:8000 wolfread-backend

## Notes

- The backend exposes API endpoints under `/api/`.

- Ensure the `.env` file is properly configured for database credentials if using a custom setup.
# RSVP Management Service

This is a simple RSVP management service built using FastAPI. The service allows users to create, read, update, and delete RSVPs for events.

## Features

- Create RSVPs for events
- Read RSVPs for specific events
- Update existing RSVPs
- Delete RSVPs

## Requirements

- Python 3.7 or higher
- FastAPI
- Uvicorn
- SQLAlchemy
- PyMySQL (for MySQL database connection)
- python-dotenv (for loading environment variables)

## Installation

1. Clone the repository:

   git clone <repository-url>
   cd rsvp-managements-service

2. Create a virtual environment:

   python -m venv venv

3. Activate the virtual environment:

   - On macOS/Linux:
     source venv/bin/activate
   - On Windows:
     .\venv\Scripts\activate

4. Install the required packages:

   pip install -r requirements.txt

5. Create a .env file in the project root directory with the following content:

   DB_USER="root"
   DB_PASSWORD="dbuserdbuser"
   DB_HOST="rsvp-management-service.cyswkjclynii.us-east-1.rds.amazonaws.com"
   DB_PORT="3306"
   DB_NAME="rsvp_management"

## Running the Application

1. Make sure your database is set up and accessible.
2. Run the FastAPI application using Uvicorn:

   uvicorn app.main:app --reload

3. Open your browser and go to http://127.0.0.1:8000 to see the application running.
4. Access the interactive API documentation at http://127.0.0.1:8000/docs.

## API Endpoints

- **GET /**: Returns a welcome message.
- **POST /events/{event_id}/rsvps/**: Create a new RSVP for an event.
- **GET /events/{event_id}/rsvps/**: Retrieve all RSVPs for a specific event.
- **GET /rsvps/{rsvp_id}**: Retrieve a specific RSVP by ID.
- **PUT /rsvps/{rsvp_id}**: Update an existing RSVP by ID.
- **DELETE /rsvps/{rsvp_id}**: Delete an RSVP by ID.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI documentation: https://fastapi.tiangolo.com/
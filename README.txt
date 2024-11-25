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

- **Documentation for EC2 Deployment of RSVP Management Service**
  - **Overview**
    - This document outlines the deployment of the RSVP Management Service on Amazon EC2.
    - It includes instructions for setup, configuration, and operational guidelines.
  
  - **Prerequisites**
    - AWS Account: Access to an AWS account with permissions to create and manage EC2 instances.
    - SSH Key Pair: A valid SSH key pair (e.g., `vockey.pem`) for accessing the EC2 instance.
    - Docker Installed: Ensure Docker is installed on the EC2 instance.
    - MySQL Database: An RDS instance or MySQL server accessible from the EC2 instance.

  - **Deployment Steps**
    1. Launch EC2 Instance:
       - Use the AWS Management Console to launch an EC2 instance.
       - Choose an appropriate Amazon Machine Image (AMI) (e.g., Amazon Linux 2).
       - Select instance type based on expected load (e.g., t2.micro for testing).
       - Configure security groups to allow inbound traffic on ports 22 (SSH) and 8000 (application).
    2. Connect to EC2 Instance:
       ```
       ssh -i "/path/to/vockey.pem" ec2-user@<EC2_PUBLIC_IP>
       ```
    3. Install Required Packages:
       ```
       sudo yum update -y
       sudo yum install docker -y
       sudo service docker start
       ```
    4. Clone Repository and Build Docker Image:
       ```
       git clone <repository-url>
       cd rsvp-management-service
       sudo docker build -t rsvp-management-service .
       ```

  - **Configuration**
    - Update the database connection string in your application code with hardcoded values or ensure environment variables are set correctly.
      Example connection string:
      ```
      DATABASE_URL = "mysql+pymysql://username:password@rsvp-management-service.cyswkjclynii.us-east-1.rds.amazonaws.com:3306/database_name"
      ```

  - **Running the Application**
    - To run the application in a Docker container:
      ```
      sudo docker run -d -p 8000:8000 rsvp-management-service
      ```
    - Access the application by navigating to:
      ```
      http://<EC2_PUBLIC_IP>:8000
      ```

  - **Monitoring and Maintenance**
    - Check application logs using:
      ```
      sudo docker logs <container_id>
      ```
    - Implement health checks to ensure that your application is running correctly.

  - **Troubleshooting**
    - If the container exits unexpectedly, check logs for error messages.
    - Ensure that security groups allow traffic on necessary ports.
    - Verify that the database is accessible from the EC2 instance.

  - **Security Considerations**
    - Regularly update your EC2 instance and installed packages.
    - Use IAM roles for accessing other AWS services securely.
    - Restrict access to your RDS instance by configuring security groups appropriately.
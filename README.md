# TeamFlow API Documentation

## Introduction

The **TeamFlow API** is a powerful REST API designed to streamline team and project management for organizations. It provides tools for creating and managing projects, assigning tasks, and fostering collaboration through real-time communication and document sharing. This allows teams to work more efficiently, ensuring smooth workflows and improved productivity.

# The API is a real-time collaboration API that enhances team productivity and streamlines project management. With tools for document sharing, task management, and seamless communication, TeamFlow enables efficient teamwork and connectivity. Secure authentication ensures all interactions are protected.

## Features

The TeamFlow API offers a wide range of features to support efficient team and project management, including:

- **Project Creation**: Easily create new projects and assign team members.
- **Task Assignment**: Assign specific tasks to team members, ensuring clarity of roles and responsibilities.
- **Document Sharing**: Share important documents and resources with team members, making necessary information easily accessible.
- **Real-Time Messaging**: Communicate instantly with team members via WebSocket, facilitating seamless collaboration.
- **User Management**: Manage team members, their roles, and their access levels within the organization.

## Getting Started

To begin using the TeamFlow API, follow these steps:

1. **Create an Organization**: Send a `POST` request to the `/auth/register` endpoint with the required information to create your organization (Anyone who creates this account is automatically the super admin of that organization).
2. **Add Team Members**: Use the `/account/create-user` endpoint to add team members by sending a `POST` request with their details.
3. **Create Projects**: Start a new project by sending a `POST` request to the `/account/create-project` endpoint. Assign team members as needed.
4. **Assign Tasks**: Allocate tasks within a project by sending a `POST` request to the `/account/create-task` endpoint with task details and the assigned team member.
5. **Share Documents**: Convert base64 PDF files into Cloudinary links, then use the `/account/upload-documents/<project_id>` endpoint to share them with the relevant team members.
6. **Send Real-Time Messages**: Communicate with team members in real-time using the WebSocket-enabled `send-message` connection.

## Running the Application Locally

To run the TeamFlow API locally using Docker:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/engrmarkk/TeamFlow.git
   cd TeamFlow
   ```

2. **Set Up Environment Variables**: Create a `.env` file in the root directory and add the following:
   ```bash
   POSTGRES_USER=<your_postgres_user>
   POSTGRES_PASSWORD=<your_postgres_password>
   POSTGRES_HOST=<your_postgres_host>
   POSTGRES_PORT=<your_postgres_port> # default is 5432
   POSTGRES_DB=<your_postgres_db>
   EMAIL_USER=<smtp_email>
   EMAIL_PASSWORD=<smtp_password>
   REDIS_HOST=redis
   REDIS_PORT=6380
   CLOUDINARY_CLOUD_NAME=<your_cloudinary_cloud_name>
   CLOUDINARY_API_KEY=<your_cloudinary_api_key>
   CLOUDINARY_API_SECRET=<your_cloudinary_api_secret>
   ```

3. **Build and Run the Docker Container**:
   ```bash
   docker-compose up --build
   ```

4. **Access the API**: The API will be available at `http://localhost` (based on the Nginx configuration).

## API Endpoints

Below are the key endpoints available in the TeamFlow API:

- **Organizations**:
  - `POST /auth/register`: Create a new organization and super admin.
  
- **Team Members**:
  - `POST /account/create-user`: Add new team members.
  
- **Projects**:
  - `POST /account/create-project`: Create new projects.
  
- **Tasks**:
  - `POST /account/create-task`: Assign tasks to team members.
  
- **Documents**:
  - `POST /account/upload-documents/<project_id>`: Share documents with team members.
  
- **Messages**:
  - `WEBSOCKET send-message`: Send real-time messages.

## Running Tests

The TeamFlow API uses [pytest](https://docs.pytest.org/en/stable/) for testing its endpoints. Follow these steps to run tests:

1. **Install pytest**:
   ```bash
   pip install pytest
   ```

2. **Run the Tests**:
   ```bash
   pytest
   ```

   Note: Before running the tests, review the test files to comment out any sections of code as necessary (as indicated in the py test file).

## Technologies Used

The following tools and technologies were utilized in the development of the TeamFlow API:

- **Flask**: Python web framework for building the API.
- **Docker**: To containerize the application for consistent environments.
- **Nginx**: For reverse proxying and load balancing.
- **Celery**: For handling asynchronous tasks.
- **PostgreSQL**: Database management.
- **Cloudinary**: For document storage and handling.
- **WebSocket**: For real-time communication.
- **pytest**: For testing the API endpoints.

## Project Structure

A simple outline of the project structure is shown below:

```
├── Dockerfile.api
├── Dockerfile.celery
├── LICENSE
├── README.md
├── app_config
│   └── __init__.py
├── celery_config
│   ├── __init__.py
│   ├── cron_job
│   │   ├── __init__.py
│   │   └── jobs.py
│   ├── schedule_config
│   │   └── __init__.py
│   └── utils
│       ├── __init__.py
│       └── cel_workers.py
├── celerybeat-schedule
├── cloudinary_config
│   └── __init__.py
├── config
│   ├── __init__.py
│   └── teamflow.sqlite
├── decorators
│   └── __init__.py
├── docker-compose.yml
├── endpoints
│   ├── __init__.py
│   ├── account.py
│   ├── authentication.py
│   └── cloudnary_route.py
├── entrypoint.sh
├── extensions
│   └── __init__.py
├── http_status
│   └── __init__.py
├── message_socket
│   └── __init__.py
├── models
│   ├── __init__.py
│   ├── admins.py
│   ├── documents.py
│   ├── messages.py
│   ├── notifications.py
│   ├── organizations.py
│   ├── projects.py
│   ├── tasks.py
│   └── users.py
├── nginx.conf
├── pusher_conn
│   ├── __init__.py
│   └── conn.py
├── requirements.txt
├── run_celery.sh
├── runserver.py
├── services
│   └── __init__.py
├── status_res
│   └── __init__.py
├── task
│   └── __init__.py
├── templates
│   ├── assigned_project.html
│   ├── document_upload.html
│   ├── expired.html
│   ├── otp.html
│   ├── pending.html
│   └── token.html
├── test
│   ├── __init__.py
│   └── test_user.py
└── utils
    └── __init__.py

```

## Conclusion

The **TeamFlow API** offers comprehensive tools to manage teams and projects, enhancing communication, collaboration, and productivity. By leveraging its powerful features, organizations can streamline their operations and achieve their objectives efficiently. Start using the TeamFlow API today to optimize your team's workflow!
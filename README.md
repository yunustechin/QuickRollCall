# Quick Roll Call

Quick Roll Call is a high-performance, secure attendance system utilizing QR codes. The project is built with a Python backend using the FastAPI framework and leverages a Redis database for high-speed data caching, session management, and rate limiting. The frontend is a lightweight, vanilla JavaScript client that interacts with the backend through a RESTful API.

The core of the system is designed for efficiency and integrity. It generates time-sensitive QR codes for each attendance session. A key feature is the implementation of a robust rate-limiting mechanism using Redis, which prevents users from submitting attendance multiple times for a single session, thereby ensuring the accuracy of attendance records.

-----

## Core Concepts and Features

  * **Secure QR Code Sessions**: The system ensures a high level of security by using a two-layered validation mechanism involving both a session ID and a one-time access token. When a student scans a QR code, they are directed to a URL containing a unique `session_id`. To access the attendance form, the frontend must first request a short-lived, single-use `access_token` associated with that session. This token is consumed upon validation, preventing it from being copied and reused by another student. Furthermore, rate-limiting is enforced on token generation and form submission, mitigating abuse and ensuring that each student can only participate once per session.

  * **Time-Limited Attendance with Redis `EXPIRE`**: To ensure that attendance is marked in a timely manner, each one-time access token has a defined lifespan managed by Redis's `EXPIRE` command. The token is configured to expire after 60 seconds. Once a token expires, it becomes invalid, preventing late or unauthorized submissions to the attendance form.

  * **High-Performance Asynchronous API**: The backend is built with **FastAPI**, a modern, high-performance web framework for Python. Its asynchronous nature, evident in the `async` function definitions throughout the codebase, ensures that the API can handle numerous concurrent requests efficiently, providing a smooth experience even with many users scanning simultaneously.

  * **Lightweight Frontend Interface**: The user interface is built with standard **HTML, CSS, and JavaScript**, utilizing the native **Fetch API** for asynchronous backend communication and the **DOM API** for dynamically rendering content. The Jinja2 templating engine serves the HTML files (`student.html`, `form.html`, `teacher.html`, `main.html`) from the backend. This approach ensures a fast-loading and universally compatible client without the need for heavy frontend frameworks.

  * **Unique QR Code and Unique Id Generator**: The system relies on securely generated unique identifiers for sessions and tokens. The `UniqueIdGenerator` class (utilized within the `SessionService`) likely employs a robust library such as Python's `secrets` module to produce cryptographically strong, unpredictable strings. These unique IDs are then used to create distinct session URLs, which are encoded into QR codes using a QR code generation library. This ensures that each attendance session is separate and that access tokens are not guessable.

  * **Data Export**: Instructors can export attendance data for any session into `.txt` or `.csv` formats. Exporting a session's data automatically closes the session in Redis, preventing any further submissions and finalizing the attendance record.

-----

## Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

  * Git
  * Docker and Docker Compose
  * Python 3.12+

### 1\. Clone the Repository

First, clone the project repository to your local machine.

```sh
git clone https://github.com/yunustechin/QuickRollCall.git
cd QuickRollCall
```

### 2\. Launch the Redis Service

The project uses a Docker container for the Redis database to ensure a consistent environment. The configuration is defined in the `docker-compose.yml` file.

Run the following command in the root of the project directory to start the Redis service in detached mode:

```sh
docker-compose up -d
```

The Redis instance will be available on `localhost:6379`.

### 3\. Install Dependencies

This project uses a `pyproject.toml` file to manage dependencies. Install them using a modern Python package installer like `pip`.

```sh
pip install .
```

This command will read the `pyproject.toml` file and install all necessary packages.

### 4\. Run the Application

The main application is run using Uvicorn, an ASGI server. The entry point is `api/main.py`.

```sh
uvicorn api.main:app --host 127.0.0.1 --port 5000 --reload
```

The API will now be running and accessible at `http://127.0.0.1:5000`. The user interface pages can be accessed via their respective endpoints.

-----

## API Endpoints

The API is logically separated into two main routers.

### QR Code and Session Management (`/qr`)

These endpoints are primarily for the instructor/teacher role.

  * **`POST /qr/generate-qr-code`**

      * **Description**: Creates a new attendance session in Redis and generates a corresponding QR code image.
      * **Response**: A `PNG` image stream of the QR code. The unique session ID is returned in the `X-Session-ID` response header.

  * **`POST /api/request-attendance-token`**

      * **Description**: Generates and returns a one-time access token for a given session, required to access the attendance form.
      * **Request Body**: A JSON object containing the `session_id`.
      * **Response**: A JSON object containing the `access_token`.

  * **`POST /qr/export/{session_id}`**

      * **Description**: Exports all student attendance records for a given session ID. This action also closes the session, preventing any further submissions.
      * **URL Parameters**: `session_id` (string, required).
      * **Query Parameters**: `format` (enum, required) - can be `txt` or `csv`.
      * **Response**: A file download (`text/plain` or `text/csv`) containing the attendance data.

### Attendance Submission (`/qr/attend`)

These endpoints are for the student role.

  * **`GET /qr/attend/{session_id}`**

      * **Description**: Displays the attendance form if the session and one-time token are valid. Access is dependent on the `validate_one_time_token` function, which consumes the token. This endpoint is rate-limited via the `enforce_rate_limit` dependency.
      * **URL Parameters**: `session_id` (string, required).
      * **Query Parameters**: `token` (string, required).
      * **Response**: An HTML page (`form.html`). Returns `403 Forbidden` if the token is invalid, `400 Bad Request` if the token doesn't match the session, and `429 Too Many Requests` if the rate limit is exceeded.

  * **`POST /qr/attend/{session_id}`**

      * **Description**: Submits a student's attendance information. The system validates that the session is still active (`validate_session_id`) and checks if the student has already submitted attendance (`has_student_submitted`) to prevent duplicates. This endpoint is also rate-limited.
      * **URL Parameters**: `session_id` (string, required).
      * **Request Body**: A JSON object containing `name`, `surname`, `school_no`, `faculty`, and `section`.
      * **Response**: A `200 OK` JSON response on success. Returns `409 Conflict` if attendance was already submitted, `410 Gone` if the session is closed, or `500 Internal Server Error` if the record could not be saved.

### Health Check Endpoints

  * **`GET /live`**
      * **Description**: A simple liveness probe to confirm the application is running.
      * **Response**: `{"status": "ok"}`.
  * **`GET /ready`**
      * **Description**: A readiness probe that checks the status of critical dependencies, specifically the connection to the Redis server.
      * **Response**: On success, `{"status": "ok", "dependencies": {"redis": "ready"}}`. On failure, returns `503 Service Unavailable`.

### User Interface Routes

The API also serves the static HTML pages for the user interface.

  * **`GET /`**: Redirects to the main application page (`/qr`).
  * **`GET /qr/`**: Serves the main application landing page (`main.html`).
  * **`GET /qr/teacher`**: Serves the teacher dashboard for creating sessions and generating QR codes (`teacher/teacher.html`).
  * **`GET /qr/attend/`**: Serves the student page which contains the QR code scanner (`student.html`).

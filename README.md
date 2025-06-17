# Quick Roll Call

Quick Roll Call is a high-performance, secure attendance system utilizing QR codes. The project is built with a Python backend using the FastAPI framework and leverages a Redis database for high-speed data caching, session management, and rate limiting. The frontend is a lightweight, vanilla JavaScript client that interacts with the backend through a RESTful API.

The core of the system is designed for efficiency and integrity. It generates time-sensitive QR codes for each attendance session. A key feature is the implementation of a robust rate-limiting mechanism using Redis, which prevents users from submitting attendance multiple times for a single session, thereby ensuring the accuracy of attendance records.

***

## Core Concepts and Features

* **Secure QR Code Sessions**: The system generates unique, single-use QR codes for each attendance session. These codes are linked to a specific session ID and are used to validate attendance submissions.

* **Time-Limited Attendance with Redis `EXPIRE`**: To ensure that attendance is marked in a timely manner, each session has a defined lifespan. This is achieved by setting an expiration time on session keys within Redis. Once a session key expires, the corresponding QR code becomes invalid, preventing late or unauthorized submissions.

* **Rate Limiting and Duplicate Entry Prevention**: A custom rate-limiting mechanism is implemented using Redis, blocking excessive requests from a single IP address. Furthermore, the system checks for existing student submissions within a session, effectively blocking any single student from marking their attendance more than once. This is critical for maintaining data integrity.

* **High-Performance Asynchronous API**: The backend is built with **FastAPI**, a modern, high-performance web framework for Python. Its asynchronous nature ensures that the API can handle numerous concurrent requests efficiently, providing a smooth experience even with many users scanning simultaneously.

* **Lightweight Frontend Interface**: The user interface is built with standard **HTML, CSS, and JavaScript**, utilizing the native **Fetch API** for asynchronous backend communication and the **DOM API** for dynamically rendering content. This approach ensures a fast-loading and universally compatible client without the need for heavy frontend frameworks.

* **Data Export**: Instructors can export attendance data for any session into `.txt` or `.csv` formats. Exporting a session's data automatically closes the session to prevent further submissions.

***

## Technology Stack

### Backend (Python)

* **Framework**: FastAPI, Uvicorn
* **Data & Caching**: Redis
* **Data Validation**: Pydantic
* **QR Code Generation**: qrcode
* **Standard Libraries**: `logging`, `functools`, `contextlib`, `json`, `traceback`, `time`, `enum`, `io`, `typing`, `datetime`, `os`, `hashlib`

### Frontend (JavaScript)

* **Core APIs**: Fetch API, DOM API

***

## Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

* Git
* Docker and Docker Compose
* Python 3.12+

### 1. Clone the Repository

First, clone the project repository to your local machine.

```sh
git clone [https://github.com/your-username/QuickRollCall.git](https://github.com/yunustechin/QuickRollCall.git)
cd your-repository-name
```

### 2. Launch the Redis Service

The project uses a Docker container for the Redis database to ensure a consistent environment. The configuration is defined in the `docker-compose.yml` file.

Run the following command in the root of the project directory to start the Redis service in detached mode:

```sh
docker-compose up -d
```

The Redis instance will be available on `localhost:6379`.

### 3. Install Dependencies

This project uses a `pyproject.toml` file to manage dependencies. Install them using a modern Python package installer like `pip`.

```sh
pip install .
```

This command will read the `pyproject.toml` file and install all necessary packages.

### 4. Run the Application

The main application is run using Uvicorn, an ASGI server. The entry point is `api/main.py`.

```sh
uvicorn api.main:app --host 127.0.0.1 --port 5000 --reload
```

The API will now be running and accessible at `http://127.0.0.1:5000`. The user interface pages can be accessed via their respective endpoints.

***

## API Endpoints

The API is logically separated into two main routers.

### QR Code and Session Management (`/qr`)

These endpoints are primarily for the instructor/teacher role.

* **`POST /qr/generate-qr-code`**
    * **Description**: Creates a new attendance session in Redis and generates a corresponding QR code image.
    * **Response**: A `PNG` image stream of the QR code. The unique session ID is returned in the `X-Session-ID` response header.

* **`POST /qr/export/{session_id}`**
    * **Description**: Exports all student attendance records for a given session ID. This action also closes the session, preventing any further submissions.
    * **URL Parameters**: `session_id` (string, required).
    * **Query Parameters**: `format` (enum, required) - can be `txt` or `csv`.
    * **Response**: A file download (`text/plain` or `text/csv`) containing the attendance data.

### Attendance Submission (`/qr/attend`)

These endpoints are for the student role.

* **`GET /qr/attend/{session_id}`**
    * **Description**: Validates a session ID from a scanned QR code. If the session is active and valid, it serves the HTML page containing the attendance submission form. This endpoint is rate-limited.
    * **URL Parameters**: `session_id` (string, required).
    * **Response**: An HTML page (`form.html`). Returns `410 Gone` if the session is expired or closed, and `429 Too Many Requests` if the rate limit is exceeded.

* **`POST /qr/attend/{session_id}`**
    * **Description**: Submits a student's attendance information. The system validates the session and checks if the student has already submitted their attendance to prevent duplicates. This endpoint is also rate-limited.
    * **URL Parameters**: `session_id` (string, required).
    * **Request Body**: A JSON object containing `name`, `surname`, `school_no`, `faculty`, and `section`.
    * **Response**: A `200 OK` JSON response on success. Returns `409 Conflict` if attendance was already submitted, or `500 Internal Server Error` if the record could not be saved.

### User Interface Routes

The API also serves the static HTML pages for the user interface.

* **`GET /`**: Health check endpoint.
* **`GET /qr/`**: Serves the main application landing page (`main.html`).
* **`GET /qr/teacher`**: Serves the teacher dashboard (`teacher.html`).
* **`GET /qr/attend/`**: Serves the student QR scanner page (`student.html`).

***

## Testing:

# YQRlama - Dynamic QR Code Attendance System

YQRlama is a modern, real-time attendance system designed for educational environments. It streamlines the attendance process by using dynamic QR codes that change periodically, ensuring students are physically present. Student information is collected efficiently and made available for export in common formats. The system is architected for scalability and robust deployment using containerization and orchestration technologies.

---

## Core Features

* **Dynamic QR Codes:** The instructor initiates an attendance session, displaying a QR code that automatically refreshes every 10 seconds to prevent sharing.
* **Student Identification:** Students enter their Name, Surname, and Student Number before scanning the QR code.
* **Real-time Data Capture:** Attendance data is captured and stored instantly upon successful QR code scan.
* **No User Registration:** Simplifies the process by not requiring prior account creation for students or instructors for session use.
* **Data Export:** Instructors can export attendance records as CSV, PDF, or Excel files.
* **Session Management:** Instructors define the duration for which the attendance session remains active.
* **Production Ready:** Built with deployment in mind using Docker, Kubernetes, and Terraform for seamless scaling and management.
* **Automated Testing & Deployment:** Integrated with CI/CD pipelines for continuous testing and reliable deployments.

---

## Technology Stack

The project leverages a modern stack for performance, scalability, and maintainability:

* **Frontend:**
    * HTML5
    * CSS3
    * JavaScript (handling QR display, student input, and QR scanning logic)
* **Backend:**
    * **Python:** for primary API development, QR code generation logic, data processing, and export functionalities.
    * **Node.js:** potentially for real-time communication aspects, or auxiliary services.
* **Database:**
    * **Redis:** Used as a NoSQL data store for managing active attendance sessions, storing dynamic QR code data, and temporarily holding attendance records before export.
* **DevOps & Deployment:**
    * **Docker:** For containerizing all application services.
    * **Kubernetes:** For orchestrating containerized applications in a production environment.
    * **Terraform:** For infrastructure as Code (IaC) to manage and provision cloud resources.
    * **CI/CD:** for automated build, test, and deployment pipelines.

---

## System Workflow

1.  **Session Initiation (Instructor):** The instructor starts an attendance session, defining its duration.
2.  **QR Code Display:** The system generates and displays a QR code. This code automatically changes every 10 seconds.
3.  **Student Interaction:**
    * The student accesses the attendance interface.
    * They input their Name, Surname, and Student Number.
    * They scan the currently displayed QR code using their device.
4.  **Data Validation & Storage:** The backend validates the QR code and student information, then records the attendance in the Redis database.
5.  **Data Export (Instructor):** After the session, the instructor can export the collected attendance data in CSV, PDF, or Excel format.

---

## Prerequisites

Ensure the following are installed on your development machine:

* Python (version 3.8+)
* Node.js (version 16+) & npm/yarn
* Docker Desktop
* kubectl (for Kubernetes interaction)
* Terraform CLI
* Redis Server (if running locally outside Docker)

---

## Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>/YQRlama.git
    cd YQRlama
    ```

2.  **Configure Environment Variables:**
    Each service (Frontend, Python Backend, Node.js Backend) may require a `.env` file. Copy the provided `.env.example` in each service directory to `.env` and update with your local or deployment-specific configurations (e.g., Redis connection details, API ports).

3.  **Backend Setup (Python):**
    Navigate to the Python backend service directory (e.g., `services/python-api`):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

4.  **Backend Setup (Node.js):**
    Navigate to the Node.js backend service directory (e.g., `services/node-service`):
    ```bash
    npm install
    # or
    # yarn install
    ```

5.  **Frontend Setup:**
    Navigate to the frontend service directory (e.g., `services/frontend`):
    ```bash
    npm install
    # or
    # yarn install
    ```

---

## Running the Project

The recommended way to run the entire stack for development is using Docker Compose.

1.  **Using Docker Compose (Recommended):**
    From the root project directory:
    ```bash
    docker-compose up --build
    ```
    This will build images for all services (frontend, Python backend, Node.js backend, Redis) and run them.

2.  **Running Services Manually (Alternative):**

    * **Start Redis:**
        Ensure Redis server is running on its default port (`6379`) or as configured. If using Docker:
        ```bash
        docker run -d -p 6379:6379 redis
        ```

    * **Start Python Backend:**
        Navigate to the Python service directory:
        ```bash
        # Example using Uvicorn for an ASGI app like FastAPI
        uvicorn main:app --reload --port 8000
        ```

    * **Start Node.js Backend:**
        Navigate to the Node.js service directory:
        ```bash
        npm start
        # or your configured run script
        ```

    * **Start Frontend:**
        Navigate to the frontend service directory:
        ```bash
        npm start
        # This usually starts a development server, e.g., on port 3000
        ```

Access the frontend application via `http://localhost:<frontend-port>` (e.g., `http://localhost:3000`).

---

## Deployment

This project is designed for production deployment using Docker and Kubernetes.

* **Docker:** `Dockerfile`s are provided for each service (frontend, Python backend, Node.js backend) to build container images.
* **Kubernetes:** Kubernetes manifest files (YAML) are included in the `/kubernetes` directory for deploying the application services, including Redis, to a Kubernetes cluster.
* **Terraform:** Terraform scripts in the `/terraform` directory can be used to provision and manage the necessary cloud infrastructure (e.g., Kubernetes cluster, networking, managed Redis instance).

Deployment typically involves building Docker images, pushing them to a container registry, and then applying the Kubernetes manifests.

---

## CI/CD Pipeline

The project is configured for Continuous Integration and Continuous Deployment (CI/CD). The pipeline includes:

1.  **Linting & Static Analysis:** Code quality checks.
2.  **Unit & Integration Tests:** Automated tests for backend and frontend components.
3.  **Build:** Building Docker images for all services.
4.  **Deployment:** Automated deployment to staging and production environments (via Kubernetes and managed by Terraform where applicable).

Refer to the CI/CD configuration file (e.g., `.gitlab-ci.yml`, `Jenkinsfile`, or GitHub Actions workflow file) in the repository for detailed steps.

---

## Data Export

Once an attendance session is complete, authorized users (instructors) can download the attendance data. This functionality is typically available through the instructor's interface on the web application. Export options include:

* **CSV (Comma Separated Values)**
* **PDF (Portable Document Format)**
* **Excel (XLSX)**

---

## Contributing

Contributions are welcome. Please fork the repository, create a feature branch, commit your changes, and open a pull request for review. Ensure your code adheres to the project's coding standards and all tests pass.

1.  Fork the Project.
2.  Create your Feature Branch (`git checkout -b feature/NewFeature`).
3.  Commit your Changes (`git commit -m 'Add some NewFeature'`).
4.  Push to the Branch (`git push origin feature/NewFeature`).
5.  Open a Pull Request.

---

## License

This project is licensed under the [MIT License]. See the `LICENSE` file for details.

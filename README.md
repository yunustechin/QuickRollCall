# YQRlama

YQRlama is a system designed to securely take attendance using QR codes. In this system, teachers generate a QR code by entering course details, and students scan the QR code to mark their attendance. The QR codes change every 15 seconds and are valid only for a specific time period. Student information is securely stored in the Redis database.

## Features
- **QR Code Generation and Scanning**: Generate dynamic QR codes and scan them.
- **Attendance**: Students scan QR codes to mark their attendance.
- **Security**: QR codes change every 15 seconds to prevent screenshots.
- **Data Storage**: Student information is securely stored in the Redis database.

## Technologies
This part will be detailed, in the draft stage

### Frontend
- **HTML**
- **CSS**
- **Bootstrap 5**
- **JavaScript**

### Backend
- **Node.js**
- **Python**
  - **Flask**
  - **Django**
  - **FastAPI**
- **PythonQR** (For generating and reading QR codes)

### Database
- **Redis**

## AWS
Currently, the project is running on **localhost** and is not open for public use. It can be hosted on **AWS** for production purposes, but as of now, it is only available for local testing. The project is ready to be deployed on AWS but is not accessible to users outside the testing phase.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

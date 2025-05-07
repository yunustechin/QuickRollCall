# YQRlama

YQRlama is a system designed to securely take attendance using QR codes. Teachers generate a unique QR code by entering course details, and students scan the QR code to mark their attendance. The QR codes change every 15 seconds and are valid only for a specific time period. Student information is securely stored in the ? database.

## Purpose

YQRlama aims to provide a secure and efficient way for teachers to manage student attendance using QR codes. This system eliminates manual attendance taking and ensures that the attendance data is securely recorded.

## Features

- **Teacher and Student Access**: 
  Teachers can generate a QR code without requiring registration. Students can scan the QR code and enter their name, surname, and school number. This information is sent to the API, and the attendance is recorded.
  
- **QR Code Generation**: 
  Teachers generate a QR code with course details, which is only valid for a limited period. The QR code changes every 15 seconds for added security.
  
- **Attendance Report**: 
  After scanning the QR code and entering their information, students' attendance data is recorded. A CSV file containing the attendance data is generated and provided to the teacher.

- **QR Code API and Backend**: 
  The backend handles the generation of dynamic QR codes, validation, and data processing for attendance recording.
  
- **Frontend Interface**: 
  The site interface is built using JavaScript and Bootstrap 5, providing an intuitive experience for both teachers and students.

- **Security Measures**: 
  - Prevents scanning the same QR code twice in succession from the same device.
  - Teachers can set the duration for which the QR code will remain valid.
  - Other security measures to prevent unauthorized access will be implemented.

## Technologies

### Frontend


### Backend


### Database


## Deployment and Container

Details for deployment and containerization will be added in the future.

## Developer Contribution

This section will be added.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

document.addEventListener("DOMContentLoaded", () => {

    const STATIC_STATUS = {
        IDLE: 'Click the button to start scanning.',
        SCANNING: 'Initializing scanner... Please point your camera at a QR code.',
        ERROR_PERMISSIONS: 'You have denied camera access. Please enable it in your browser setting and refresh the page to use the scanner.',
        ERROR_NOT_FOUND: 'No camera found on this device. You can try uploading a QR code image instead.',
        ERROR_START_GENERIC: 'Failed to start the scanner. Please check your hardware and try again.',
        ERROR_STOP: 'Failed to stop the scanner after a successful scan.',
        INFO_FILE_SCAN: 'Scanning the selected image for a QR code...',
        ERROR_FILE_SCAN: 'No QR code found in the selected image. Please try another one.',
        ERROR_HTTPS: 'This application requires HTTPS to access the camera.'
    };

    const DYNAMIC_STATUS = {
        SUCCESS: (text) => `Scan successful: ${text}`,
    };

    const scanButton = document.getElementById('scanButton');
    const readerDiv = document.getElementById('reader');
    const statusDiv = document.getElementById('status');
    const html5QrCode = new Html5Qrcode("reader");

    function showIdleState() {
        readerDiv.style.display = 'none';
        scanButton.style.display = 'block';
    }

    function isHTTPS() {
         return window.location.protocol === 'https:' || window.location.hostname === 'localhost' || window.location.hostname === '192.168.1.6';
    }

    async function handleScanSuccess(decodedText) {
        try {
            await html5QrCode.stop();
            showIdleState();
        } catch (err) {
            console.error("Failed to stop scanner:", err);
            statusDiv.textContent = "Failed to stop scanner.";
        }
        
        const urlParts = decodedText.split('/');
        const sessionId = urlParts[urlParts.length - 1];

        if (!sessionId) {
            statusDiv.textContent = "Invalid QR Code format. Session ID not found.";
            return;
        }

        statusDiv.textContent = `Session ${sessionId} found. Requesting access...`;

        try {
            const response = await fetch('/qr/api/request-attendance-token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ session_id: sessionId }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to get access token.');
            }

            const data = await response.json();

            if(!data.access_token){
                throw new Error('Token not found in response.');
            }

            statusDiv.textContent = "Access granted. Redirecting...";
            window.location.href = `/qr/attend/${sessionId}?token=${data.access_token}`;

        } catch (error) {
            console.error('Error fetching access token:', error);
            statusDiv.textContent = `Error: ${error.message}. Please try again.`;
        }
    }

    async function startScanner() {
        scanButton.style.display = 'none';
        readerDiv.style.display = 'block';
        statusDiv.textContent = STATIC_STATUS.SCANNING;

        const config = {
            fps: 10,
            qrbox: { width: 250, height: 250 } 
        };

        try {
            await html5QrCode.start(
                { facingMode: "environment" },
                config,
                handleScanSuccess
            );
        } catch (err) {
            console.error(STATIC_STATUS.ERROR_START_GENERIC, err);
            statusDiv.textContent = STATIC_STATUS.ERROR_START_GENERIC;
            showIdleState();
        }
    }

    function initialize() {
        if (!isHTTPS()) {
            statusDiv.textContent = STATIC_STATUS.ERROR_HTTPS;
            scanButton.disabled = true;
            return;
        }

        scanButton.addEventListener('click', startScanner);
        statusDiv.textContent = STATIC_STATUS.IDLE;
    }

    initialize();
});

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
         return window.location.protocol === 'https:' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    }

    async function handleScanSuccess(decodedText) {
        try {
            await html5QrCode.stop();
            showIdleState();
            statusDiv.textContent = DYNAMIC_STATUS.SUCCESS(decodedText);

            // TODO: Route veya API logic buraya yazılacak

        } catch (err) {
            console.error(STATIC_STATUS.ERROR_STOP, err);
            statusDiv.textContent = STATIC_STATUS.ERROR_STOP;
        }
    }

    function handleScanFailure(_errorMessage) {
        // Minor bug — logging will be done for performance
        // console.warn(`QR Code scan failure: ${_errorMessage}`);
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
                handleScanSuccess,
                handleScanFailure
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

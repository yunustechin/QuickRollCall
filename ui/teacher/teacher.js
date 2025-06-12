document.addEventListener('DOMContentLoaded', () => {

    const API_URL = 'http://127.0.0.1:5000/qr/generate-qr-code';
    const ALT_TEXT = {
        LOADING: 'Generating QR Code...',
        SUCCESS: 'QR Code Image',
        ERROR: 'Failed to generate QR Code.'
    };

    const generateButton = document.getElementById('generateButton');
    const qrImageElement = document.getElementById('qrImage');

    /**
     * Fetches a QR code image from the API.
     * @returns {Promise<Blob>} A promise that resolves with the image blob.
     * @throws {Error} If the network response is not successful.
     */
    const fetchQrCode = async () => {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Accept': 'image/png'
            }
        });

        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }

        return response.blob();
    };

    /**
     * Handles the click event to generate and display a new QR code.
     * This function orchestrates the UI updates and the API call.
     */
    const handleGenerateClick = async () => {
        // 1. Set the UI to a loading state
        qrImageElement.src = '';
        qrImageElement.alt = ALT_TEXT.LOADING;

        try {
            // 2. Fetch the QR code image data
            const imageBlob = await fetchQrCode();
            const imageUrl = URL.createObjectURL(imageBlob);

            // 3. Display the generated image on success
            qrImageElement.src = imageUrl;
            qrImageElement.alt = ALT_TEXT.SUCCESS;

        } catch (error) {
            // 4. Handle any errors during the process
            console.error('QR Code generation failed:', error);
            qrImageElement.alt = ALT_TEXT.ERROR;
        }
    };

    generateButton.addEventListener('click', handleGenerateClick);

});
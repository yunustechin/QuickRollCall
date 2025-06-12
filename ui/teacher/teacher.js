document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://127.0.0.1:5000/qr/generate-qr-code';
    const ALT_TEXT = {
        LOADING: 'Generating QR Code...',
        SUCCESS: 'QR Code Image',
        ERROR: 'Failed to generate QR Code.'
    };

    const generateButton = document.getElementById('generateButton');
    const qrImageElement = document.getElementById('qrImage');

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

    const handleGenerateClick = async () => {
        qrImageElement.src = '';
        qrImageElement.alt = ALT_TEXT.LOADING;

        try {
            const imageBlob = await fetchQrCode();
            const imageUrl = URL.createObjectURL(imageBlob);

            qrImageElement.src = imageUrl;
            qrImageElement.alt = ALT_TEXT.SUCCESS;

        } catch (error) {
            console.error('QR Code generation failed:', error);
            qrImageElement.alt = ALT_TEXT.ERROR;
        }
    };

    generateButton.addEventListener('click', handleGenerateClick);
});
document.addEventListener('DOMContentLoaded', () => {

    const generateButton = document.getElementById('generateButton')
    const qrImageElement = document.getElementById('qrImage');
    const apiUrl = 'http://127.0.0.1:5000/qr/generate-qr-code';

    generateButton.addEventListener('click', async () => {
        qrImageElement.src = '';
        qrImageElement.alt = 'Generating QR Code...';

        try {
            // API POST request to generate QR code
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Accept': 'image/png'
                }
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            // Convert the returned blob to an image URL and append it to the DOM
            const imageBlob = await response.blob();
            const imageUrl = URL.createObjectURL(imageBlob);
            qrImageElement.src = imageUrl;
            qrImageElement.alt = 'QR Code';

        } catch (error) {
            console.error('There was a problem with the fetch operation:', error);
            qrImageElement.alt = 'Error generating QR Code';
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {

    // Button and image elements selection
    const generateButton = document.getElementById('generateButton')
    const qrImageElement = document.getElementById('qrImage');

    // API endpoint for generating QR code
    const apiUrl = 'http://127.0.0.1:5000/qr/generate-qr-code';

    // User triggers QR code generation
    generateButton.addEventListener('click', async () => {

        // Clear previous QR code image and alt text update
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

            // Response is expected to be a blob (image)
            const imageBlob = await response.blob();

            // Create a local URL for the image blob and set it as the source of the image element
            const imageUrl = URL.createObjectURL(imageBlob);
            qrImageElement.src = imageUrl;
            qrImageElement.alt = 'QR Code';

        } catch (error) {
            console.error('There was a problem with the fetch operation:', error);
            qrImageElement.alt = 'Error generating QR Code';
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    
    const GENERATE_API_URL = '/qr/generate-qr-code';
    const EXPORT_API_URL_BASE = '/qr/export';

    const ALT_TEXT = {
        LOADING: 'Generating QR Code...',
        SUCCESS: 'Attendance QR Code',
        ERROR: 'Failed to generate QR Code.',
        PLACEHOLDER: 'QR Code will appear here'
    };

    const generateButton = document.getElementById('generateButton');
    const qrImageElement = document.getElementById('qrImage');
    const exportControls = document.getElementById('exportControls');
    const exportButton = document.getElementById('responseButton');
    const formatSelector = document.getElementById('formatSelector');

    let currentSessionId = null;

    const handleGenerateClick = async () => {   
        qrImageElement.src = '';
        qrImageElement.alt = ALT_TEXT.LOADING;
        exportControls.style.display = 'none';
        generateButton.disabled = true;
        currentSessionId = null;


        try {
            const response = await fetch(GENERATE_API_URL, {
                method: 'POST',
                headers: {
                    'Accept': 'image/png'
                }
            });

            if (!response.ok) {
                throw new Error(`API request failed with status ${response.status}`);
            }

            const sessionId = response.headers.get('X-Session-ID');
            if (!sessionId) {
                throw new Error('Session ID was not provided by the server.');
            }
            currentSessionId = sessionId;
            console.log(`Session ID received: ${currentSessionId}`);

            const imageBlob = await response.blob();
            const imageUrl = URL.createObjectURL(imageBlob);

            qrImageElement.src = imageUrl;
            qrImageElement.alt = ALT_TEXT.SUCCESS;

            generateButton.style.display = 'none';
            exportControls.style.display = 'block';

        } catch (error) {
            console.error('QR Code generation failed:', error);
            qrImageElement.alt = ALT_TEXT.ERROR;
            generateButton.disabled = false;
            generateButton.textContent = 'Generate QR Code';
        }
    };

    const handleExportClick = async () => {
        if (!currentSessionId) {
            alert('Cannot export: No active session ID.');
            return;
        }

        const selectedFormat = formatSelector.value;
        const exportUrl = `${EXPORT_API_URL_BASE}/${currentSessionId}?format=${selectedFormat}`;
        
        exportButton.disabled = true;
        exportButton.textContent = 'Exporting...';
         try {
            const response = await fetch(exportUrl, {
                method: 'POST'
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData?.detail || `Export failed with status ${response.status}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            
            a.style.display = 'none';
            a.href = url;
            
            const date = new Date().toISOString().split('T')[0];
            a.download = `rollcall_${date}.${selectedFormat}`;
            
            document.body.appendChild(a);
            a.click();
            
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

        } catch (error) {
            console.error('Export failed:', error);
            alert(`Error during export: ${error.message}`);
        } finally {
            exportButton.disabled = false;
            exportButton.textContent = 'Export';
        }
    };

    generateButton.addEventListener('click', handleGenerateClick);
    exportButton.addEventListener('click', handleExportClick);
});
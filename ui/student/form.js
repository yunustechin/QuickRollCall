document.getElementById('attendanceForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const sessionId = document.getElementById('session_id').value;
    const messageDiv = document.getElementById('message');
    const formData = {
        name: document.getElementById('name').value,
        surname: document.getElementById('surname').value,
        school_no: document.getElementById('school_no').value,
        faculty: document.getElementById('faculty').value,
        section: document.getElementById('section').value
    };

    try {
        const response = await fetch(`/qr/attend/${sessionId}`, {
            method: 'POST',
            headers: {
                 'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
                
        const result = await response.json();

        if (!response.ok){
            messageDiv.style.color = 'red';
            messageDiv.textContent = result.detail || 'An unknown error occurred.';
        }
        
        messageDiv.style.color = 'green';
        messageDiv.textContent = result.message;
        document.getElementById('attendanceForm').classList.add('hidden');

    } catch (error) {
        messageDiv.style.color = 'red';
        messageDiv.textContent = 'Failed to submit form. Please check your connection.';
        console.error('Error submitting form:', error);
    }
});
import qrcode
import hashlib
import time

class UniqueIdGenerator:
    def __init__(self):
        self.unique_id = self.generate_unique_id()

    def generate_unique_id(self):
        """Generate a unique ID based on the current time and a random number."""
        return hashlib.sha256(f"{time.time()}".encode()).hexdigest()

    def get_unique_id(self):
        """Return the unique ID."""
        return self.unique_id
    
class QRCodeGenerator:
    def __init__(self, data):
        self.data = data
        self.qr_code = None

    def generate_qr_code(self):
        """Generate a QR code from the provided data."""
        self.qr_code = qrcode.make(self.data)

    def save_qr_code(self, filename):
        """Save the generated QR code to a file."""
        if self.qr_code:
            self.qr_code.save(filename)
        else:
            raise ValueError("QR code not generated yet.")
        
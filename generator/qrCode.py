import qrcode
import hashlib
import time

class UniqueIdGenerator:
    def __init__(self):
        self.unique_id = self.generate_unique_id()

    def generate_unique_id(self) -> str:
        """
        Generate a unique SHA-256 hash based on the current time.

        Returns:
            str: A hexadecimal string representing the unique ID.
        """
        return hashlib.sha256(f"{time.time()}".encode()).hexdigest()

    def get_unique_id(self) -> str:
        return self.unique_id
    
class QRCodeGenerator:
    def __init__(self, data: str) -> None:
        self.data = data
        self.qr_code = None

    def generate_qr_code(self) -> None:
        """
        Generate a QR code from the provided data.

        This method stores the QR code internally; it must be called before saving.
        """
        self.qr_code = qrcode.make(self.data)

    def save_qr_code(self, filename: str) -> None:
        """
        Save the generated QR code to a PNG file.

        Args:
            filename (str): The path to save the QR code image.

        Raises:
            ValueError: If the QR code has not been generated yet.
        """
        if self.qr_code:
            self.qr_code.save(filename)
        else:
            raise ValueError("QR code not generated yet.")
        
import qrcode
import secrets

class UniqueIdGenerator:

    @staticmethod
    def generate() -> str:
        """
        Generate a secure random unique ID.

        Returns:
            str: A 64-character hexadecimal unique ID.
        """
        return secrets.token_hex(32)


class QRCodeGenerator:

    @staticmethod
    def generate(data: str):
        """
        Generate a QR code image for the given data.

        Args:
            data (str): The data to encode in the QR code.

        Returns:
            PIL.Image.Image: The generated QR code image.
        """
        return qrcode.make(data)

    @staticmethod
    def save(image, buffer, format: str) -> None:
        """
        Save the QR code image to a PNG file.

        Args:
            image (PIL.Image.Image): The QR code image to save.
            buffer: The file-like object or filename to save the image to.
        """
        if image is None:
            raise ValueError("No QR code image to save.")
        image.save(buffer, format)

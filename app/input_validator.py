from PIL import Image


class InputValidator:
    """Checks the input before it is sent to a diagnosis service.

    Every check returns a short plain message when something is wrong,
    and None when the input is fine.
    """

    ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png")
    ALLOWED_FORMATS = ("JPEG", "PNG")
    MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB

    MSG_NO_FILE = "Please choose a photo to upload."
    MSG_WRONG_TYPE = "This file type is not supported. Please upload a JPEG or PNG photo."
    MSG_TOO_LARGE = "This photo is too large. Please upload a photo of 10 MB or less."
    MSG_NOT_AN_IMAGE = "This file could not be read as a photo. Please upload a different JPEG or PNG photo."
    MSG_EMPTY_TEXT = "Please describe the symptoms you see."

    def check_image(self, file):
        """Return a message if the image is not acceptable, otherwise None."""
        if file is None:
            return self.MSG_NO_FILE

        name = (getattr(file, "name", "") or "").lower()
        if not name.endswith(self.ALLOWED_EXTENSIONS):
            return self.MSG_WRONG_TYPE

        if self._size_of(file) > self.MAX_IMAGE_BYTES:
            return self.MSG_TOO_LARGE

        if not self._is_real_image(file):
            return self.MSG_NOT_AN_IMAGE

        return None

    def check_text(self, text):
        """Return a message if the text is empty, otherwise None."""
        if text is None or not text.strip():
            return self.MSG_EMPTY_TEXT
        return None

    def _size_of(self, file):
        """Measure the file in bytes, then rewind it to the start."""
        file.seek(0, 2)  # move to the end of the file
        size = file.tell()
        file.seek(0)
        return size

    def _is_real_image(self, file):
        """Try to open the file as an image. Always rewind it afterwards."""
        try:
            file.seek(0)
            image = Image.open(file)
            image_format = image.format
            image.verify()
            return image_format in self.ALLOWED_FORMATS
        except Exception:
            return False
        finally:
            file.seek(0)  # leave the file ready for the image service
import pytesseract
from PIL import Image
from plugins.abstract_plugin import AbstractPlugin

class OCRExtractor(AbstractPlugin):
    """
    This plugin extracts text from images using OCR.
    """
    def __init__(self):
        super().__init__(
            authors=["ef1500"],
            description="Extracts text from images using OCR",
            version="1.0",
            category=["extractor"],
            associated_file_extensions=[".jpg", ".png"]
        )

    def process_document(self, full_path, filename, creation_date, last_modified_date, file_ext,
                         filesize, import_time):
        if file_ext not in self.associated_file_extensions:
            # Not an image file, skip processing
            return

        # Use pytesseract to extract text from image
        image = Image.open(full_path)
        text = pytesseract.image_to_string(image)

        # Return extracted text as JSON
        return {
            self.plugin_name: {
                "data": {
                    "text": text
                },
                "source": filename
            }
        }
import os
import time
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from pdf2image import convert_from_path
import pytesseract
from pytesseract import Output

from .models import UserDocument
from .utilities import document_text_path

logger = logging.getLogger(__name__)


def verify_document(document_id: int):
    document = update_document_status(document_id, db_status='in_progress', frontend_status='В обработке')

    # Verification process placeholder
    # time.sleep(10)
    recognizer = UserDocumentRecognizer(document)
    recognizer.recognize()

    update_document_status(document_id, db_status='approved', frontend_status='Одобрен')


def update_document_status(document_id: int, db_status: str, frontend_status: str):
    """
    Update status in db and send it through WebSocket
    """
    document = UserDocument.update_status_by_id(document_id, db_status)
    async_to_sync(document_status_send)(document.user.id, document_id, frontend_status)
    return document


async def document_status_send(user_id: int, document_id: int, new_status: str, channel_layer=None):
    if not channel_layer:
        channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f'user_{user_id}_document_update',  # Group
        {
            'type': 'document.status.update',  # Method of consumer
            'document_id': document_id,
            'new_status': new_status
        }
    )


class UserDocumentRecognizer:
    def __init__(self, document: UserDocument):
        logger.info(f'User: {document.user.id}. Document: "{document.document_name}". Recognition process is started')
        self.document = document
        self.text_path = self.set_text_path(document)
        self.page_title = f'# Page:'
        # Path to Tesseract executable, if not in std path
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
        self.poppler_path = '/usr/bin'

    def recognize(self):
        # Convert PDF to list of images (per page)
        images = convert_from_path(self.document.file.path, poppler_path=self.poppler_path)
        for i, image in enumerate(images):
            current_page_title = f'{self.page_title}{i + 1}'
            logger.info(f'Recognition of {current_page_title}...')

            orientation = pytesseract.image_to_osd(image, output_type=Output.DICT)
            rotated_image = image.rotate(-orientation["rotate"], expand=True)
            logger.debug(f'{orientation=}')

            orientation_rotated = pytesseract.image_to_osd(rotated_image, output_type=Output.DICT)
            logger.debug(f'{orientation_rotated=}')

            raw_text = pytesseract.image_to_string(rotated_image, lang='rus')
            cleaned_text = '\n'.join(filter(bool, raw_text.split('\n')))
            logger.debug(cleaned_text)

            self.append_text_to_file(current_page_title, cleaned_text)

    def append_text_to_file(self, current_page_title: str, text: str):
        with open(self.text_path, 'a') as f:
            f.write(f'\n\n\n{current_page_title}\n')
            f.write(text)

    @staticmethod
    def set_text_path(document):
        text_path = document_text_path(document)
        directory = os.path.dirname(text_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(text_path, 'w'):
            pass
        logger.debug(f'{text_path=}')
        return text_path


class UserDocumentVerifier:
    def __init__(self):
        pass

    def get_status(self):
        pass



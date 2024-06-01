import os
import time
import logging

import cv2
import numpy as np
from PIL.Image import Image
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from pdf2image import convert_from_path
import pytesseract
from pytesseract import Output, TesseractError
from pymystem3 import Mystem

from .models import UserDocument
from .utilities import document_text_path


def verify_document(document_id: int):
    document = update_document_status(document_id, db_status='in_progress', frontend_status='В обработке')
    logger = logging.getLogger(__name__)

    # Verification process placeholder
    recognizer = UserDocumentRecognizer(document, logger)
    recognizer.recognize()
    document_txt_path = recognizer.text_path
    user = document.user
    fio_status = verify_user_fio(document_txt_path, user, logger)
    if fio_status:
        update_document_status(document_id, db_status='approved', frontend_status='Одобрен')
    else:
        update_document_status(document_id, db_status='verification_failed', frontend_status='Проверка не пройдена')


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
    def __init__(self, document: UserDocument, logger):
        self.document = document
        self.logger = logger
        self.logger.info(f'User: {document.user.id}.'
                         f' Document: "{document.document_name}". Recognition process is started')
        self.text_path = self.set_text_path(document)
        self.page_title = f'# Page:'
        # Path to Tesseract executable, if not in std path
        pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
        self.poppler_path = '/usr/bin'

    def recognize(self):
        # Convert PDF to list of images (per page)
        images = convert_from_path(self.document.file.path, poppler_path=self.poppler_path)
        try:
            self.recognize_images(images)
        except TesseractError as e:
            self.logger.debug(f'{e}')
            self.retry(images, rotation_method='haff', tesseract_config='--psm 3 --dpi 300 -l rus')
        self.logger.info(f'User: {self.document.user.id}.'
                         f' Document: "{self.document.document_name}". Recognition process ended')

    def recognize_images(self, images: list, rotation_method='osd', tesseract_config=''):
        for i, image in enumerate(images):
            current_page_title = f'{self.page_title}{i + 1}'
            self.logger.info(f'Recognition of "{self.document.document_name}" {current_page_title}...')
            if rotation_method == 'osd':
                image = self.osd_rotate(image)
            elif rotation_method == 'haff':
                image = self.haff_rotate(image)
            else:
                raise AttributeError('Wrong recognize_images() rotation_method')
            raw_text = pytesseract.image_to_string(image, lang='rus', config=tesseract_config)
            cleaned_text = '\n'.join(filter(bool, raw_text.split('\n')))
            self.logger.debug(f'Document text:\n{cleaned_text}')

            self.append_text_to_file(current_page_title, cleaned_text)

    def osd_rotate(self, image) -> Image:
        orientation = pytesseract.image_to_osd(image, output_type=Output.DICT)
        rotated_image = image.rotate(-orientation["rotate"], expand=True)
        self.logger.debug(f'{orientation=}')

        orientation_rotated = pytesseract.image_to_osd(rotated_image, output_type=Output.DICT)
        self.logger.debug(f'{orientation_rotated=}')
        return rotated_image

    def haff_rotate(self, image):
        image_matrix = np.array(image)
        gray_image = cv2.cvtColor(image_matrix, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

        # Angle with the most quantity of lines finding
        angles = []
        for line in lines:
            for rho, theta in line:
                angle = np.rad2deg(theta)
                angles.append(angle)
        angles = np.round(angles)

        # The most frequent angle finding
        unique, counts = np.unique(angles, return_counts=True)
        most_frequent_angle = unique[np.argmax(counts)]

        self.logger.debug(f'Haff Algorythm: The most frequent angle: {most_frequent_angle} deg.')
        rotated_image = image.rotate(most_frequent_angle + 90)
        return rotated_image

    def append_text_to_file(self, current_page_title: str, text: str):
        with open(self.text_path, 'a') as f:
            f.write(f'\n\n\n{current_page_title}\n')
            f.write(text)

    def retry(self, *args, **kwargs):
        self.recognize_images(*args, **kwargs)

    @staticmethod
    def set_text_path(document):
        text_path = document_text_path(document)
        directory = os.path.dirname(text_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(text_path, 'w'):
            pass
        return text_path


def verify_user_fio(text_path, user: settings.AUTH_USER_MODEL, logger):
    with open(text_path, 'r') as f:
        text = f.read()
    analyzer = FioAnalyser()
    analysed = analyzer.analyze(text)
    analyzer.extract_fio(analysed)
    fio = analyzer.get_detailed_fio()
    logger.debug(f'Extracted {fio=}')

    name_part_statuses = {}
    for name_part_key, properties in fio.items():
        name_part = getattr(user, name_part_key)
        if properties['lexeme'] == name_part.lower():
            name_part_statuses[name_part] = True
        else:
            name_part_statuses[name_part] = False

    fio_status = False
    if all(name_part_statuses.values()):
        fio_status = True
    else:
        logger.debug(f'{name_part_statuses=}')
    return fio_status


class UserDocumentVerifier:
    def __init__(self):
        pass

    def get_status(self):
        pass


class FioAnalyser:
    def __init__(self):
        self.analyser = Mystem()
        self._fio = {
            'first_name': {'alias': 'имя', 'lexeme': None, 'confidence': 0, },
            'last_name': {'alias': 'фам', 'lexeme': None, 'confidence': 0, },
            'patronymic': {'alias': 'отч', 'lexeme': None, 'confidence': 0, },
        }

    def analyze(self, text) -> list:
        analysed = self.analyser.analyze(text)
        return analysed

    def extract_fio(self, analysed: list) -> dict:
        for item in analysed:
            analyses = item.get('analysis')
            if analyses:
                analysis = analyses[0]
                grammar = analysis.get('gr', '')
                word = analysis.get('lex')
                confidence = analysis.get('wt')
                self.set_name_part('first_name', grammar, word, confidence)
                self.set_name_part('last_name', grammar, word, confidence)
                self.set_name_part('patronymic', grammar, word, confidence)
        return self.get_simple_fio()

    def set_name_part(self, part: str, grammar, word: str, confidence: float):
        fio_part = self._fio[part]
        if fio_part['alias'] in grammar:
            if confidence > fio_part['confidence']:
                fio_part['confidence'] = confidence
                fio_part['lexeme'] = word

    def get_simple_fio(self):
        return {part: self._fio[part]['lexeme'] for part in self._fio.keys()}

    def get_detailed_fio(self):
        return self._fio



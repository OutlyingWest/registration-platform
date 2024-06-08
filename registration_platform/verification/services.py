import os
import time
import logging

import cv2
import numpy as np
from PIL.Image import Image
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from pdf2image import convert_from_path
import pytesseract
from pytesseract import Output, TesseractError
from pymystem3 import Mystem

from .models import UserDocument
from .utilities import build_document_text_path


logger = logging.getLogger(__name__)


def verify_document(document_id: int):
    update_document_status(document_id, db_status='in_progress', frontend_status='В обработке')

    recognizer = UserDocumentRecognizer(document_id)
    recognizer.extract_text()
    verifier = UserFullNameVerifier(document_id)
    is_user_full_name_ok = verifier.verify()
    if is_user_full_name_ok:
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
    def __init__(self, document_id: int):
        self.document = UserDocument.objects.get(id=document_id)
        logger.info(f'User: {self.document.user.id}.'
                    f' Document: "{self.document.document_name}". Recognition process is started')
        self.text_path = self.set_text_path(self.document)
        self.page_title = f'# Page:'
        # Path to Tesseract executable, if not in std path
        pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
        self.poppler_path = '/usr/bin'

    def extract_text(self):
        # Convert PDF to list of images (per page)
        images = convert_from_path(self.document.uploaded_file.path, poppler_path=self.poppler_path)
        try:
            self.recognize_images(images)
        except TesseractError as e:
            logger.debug(f'{e}')
            self.retry(images, rotation_method='haff', tesseract_config='--psm 3 --dpi 300 -l rus')
        logger.info(f'User: {self.document.user.id}.'
                    f' Document: "{self.document.document_name}". Recognition process ended')

    def recognize_images(self, images: list, rotation_method='osd', tesseract_config=''):
        for i, image in enumerate(images):
            current_page_title = f'{self.page_title}{i + 1}'
            logger.info(f'Recognition of "{self.document.document_name}" {current_page_title}...')
            if rotation_method == 'osd':
                image = self.osd_rotate(image)
            elif rotation_method == 'haff':
                image = self.haff_rotate(image)
            else:
                raise AttributeError('Wrong recognize_images() rotation_method')
            raw_text = pytesseract.image_to_string(image, lang='rus', config=tesseract_config)
            cleaned_text = '\n'.join(filter(bool, raw_text.split('\n')))
            logger.debug(f'Document text:\n{cleaned_text}')

            self.append_text_to_file(current_page_title, cleaned_text)

    def osd_rotate(self, image) -> Image:
        orientation = pytesseract.image_to_osd(image, output_type=Output.DICT)
        rotated_image = image.rotate(-orientation['rotate'], expand=True)
        logger.debug(f'{orientation=}')

        orientation_rotated = pytesseract.image_to_osd(rotated_image, output_type=Output.DICT)
        logger.debug(f'{orientation_rotated=}')
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

        logger.debug(f'Haff Algorythm: The most frequent angle: {most_frequent_angle} deg.')
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
        text_path = build_document_text_path(document)
        media_text_path = os.path.join(settings.MEDIA_ROOT, text_path)

        document.extracted_text_file = ContentFile(b'', name=media_text_path)
        document.save()
        return media_text_path

    def get_text_path(self):
        if self.text_path:
            return self.text_path
        else:
            raise ValueError('Text path is empty')


class UserFullNameVerifier:
    def __init__(self, document_id: int):
        self.document = UserDocument.objects.get(id=document_id)

    def verify(self):
        extracted_full_name = self.extract_full_name()
        is_full_name_ok = self.compare_extracted_full_name_with_document_owner(extracted_full_name)
        return is_full_name_ok

    def extract_full_name(self):
        with open(self.document.extracted_text_file.path, 'r') as f:
            text = f.read()
        analyzer = FullNameAnalyser()
        analysed = analyzer.analyze(text)
        analyzer.extract_full_name(analysed)
        extracted_full_name = analyzer.get_detailed_full_name()
        logger.debug(f'Extracted {extracted_full_name=}')
        return extracted_full_name

    def compare_extracted_full_name_with_document_owner(self, full_name: dict):
        user = self.document.user
        name_part_statuses = {}
        for name_part_key, properties in full_name.items():
            name_part = getattr(user, name_part_key)
            if properties['lexeme'] == name_part.lower():
                name_part_statuses[name_part] = True
            else:
                name_part_statuses[name_part] = False

        is_full_name_ok = False
        if all(name_part_statuses.values()):
            is_full_name_ok = True
        else:
            logger.debug(f'{name_part_statuses=}')
        return is_full_name_ok


class FullNameAnalyser:
    def __init__(self):
        self.analyser = Mystem()
        self._full_name = {
            'first_name': {'alias': 'имя', 'lexeme': None, 'confidence': 0, },
            'last_name': {'alias': 'фам', 'lexeme': None, 'confidence': 0, },
            'patronymic': {'alias': 'отч', 'lexeme': None, 'confidence': 0, },
        }

    def analyze(self, text) -> list:
        analysed = self.analyser.analyze(text)
        return analysed

    def extract_full_name(self, analysed: list) -> dict:
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
        return self.get_simple_full_name()

    def set_name_part(self, part: str, grammar, word: str, confidence: float):
        fio_part = self._full_name[part]
        if fio_part['alias'] in grammar:
            if confidence > fio_part['confidence']:
                fio_part['confidence'] = confidence
                fio_part['lexeme'] = word

    def get_simple_full_name(self):
        return {part: self._full_name[part]['lexeme'] for part in self._full_name.keys()}

    def get_detailed_full_name(self):
        return self._full_name

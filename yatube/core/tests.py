from http import HTTPStatus

from django.conf.urls import handler404
from django.test import TestCase


class ErrorURLTest(TestCase):
    def test_unexicting_page(self):
        """Несуществующая страница возвращает ошибку 404."""
        response = self.client.get(handler404)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

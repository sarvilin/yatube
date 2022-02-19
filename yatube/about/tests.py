from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_allguests_page_access(self):
        """Проверка доступности страниц не требующих авторизации"""
        correct_values = {
            '/about/author/': 200,
            '/about/tech/': 200,
        }
        for address, expected_value in correct_values.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    response.status_code,
                    expected_value,
                    f'Тест доступности страницы {address} '
                    'для анонимного пользователя провален'
                )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

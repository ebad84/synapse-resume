"""Regression tests: python -m unittest discover -s tests -v"""
import unittest
from unittest.mock import patch
from app import app, resume_projects


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_public_routes(self):
        for route in ('/', '/fa', '/more', '/fa/more', '/api/projects'):
            with self.subTest(route=route):
                self.assertEqual(self.client.get(route).status_code, 200)
        self.assertEqual(self.client.get('/teapot').status_code, 418)
        self.assertEqual(self.client.get('/unknown-language').status_code, 404)

    def test_server_rendered_content_and_cat(self):
        for route, language, direction in (('/', 'en', 'ltr'), ('/fa', 'fa', 'rtl')):
            page = self.client.get(route).get_data(as_text=True)
            for expected in (f'lang="{language}"', f'dir="{direction}"', 'profile.jpg', 'iso-toggle', 'oneko.js', 'data-cat="/static/oneko.gif"', 'id="experience"', 'id="about"', 'id="projects"'):
                self.assertIn(expected, page)
            self.assertEqual(page.count('data-category='), 7)
            self.assertNotIn('built-in method', page)
            self.assertIn('2026-present', page)
            self.assertIn('2020-2024', page)

    def test_software_first_without_mutating_stored_records(self):
        original = [{'id': 'board', 'tags': ['ESP32']}, {'id': 'app', 'tags': ['FLASK']}]
        with patch('app.load_projects', return_value=original):
            rows = resume_projects()
        self.assertEqual([p['id'] for p in rows], ['app', 'board'])
        self.assertNotIn('category', original[0])

    def test_content_escaping_and_unsafe_links(self):
        project = {'title': {'en': '<script>alert(1)</script>'}, 'desc': {'en': '<img src=x onerror=alert(1)>'}, 'tags': ['FLASK'], 'link': 'javascript:alert(1)', 'image': None}
        with patch('app.load_projects', return_value=[project]):
            page = self.client.get('/').get_data(as_text=True)
        self.assertIn('&lt;script&gt;', page)
        self.assertNotIn('href="javascript:', page)
        self.assertNotIn('<img src=x', page)

    def test_empty_projects_and_existing_api(self):
        with patch('app.load_projects', return_value=[]):
            page = self.client.get('/').get_data(as_text=True)
            self.assertIn('No projects yet.', page)
            self.assertEqual(self.client.get('/api/projects').json, {'projects': []})

    def test_admin_still_requires_authentication(self):
        self.assertEqual(self.client.get('/admin/content').status_code, 401)
        self.assertEqual(self.client.get('/admin/projects').status_code, 401)

    def test_secondary_cat_sprite_path(self):
        for route in ('/more', '/fa/more'):
            self.assertIn('data-cat="/static/oneko.gif"', self.client.get(route).get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()

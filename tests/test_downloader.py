import sys
import os
import unittest
from unittest.mock import patch, mock_open, Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from downloader import *
class TestUpdateLocalLinks(unittest.TestCase):
    
    def setUp(self):
        self.base_url = "http://example.com"
        self.local_path = "site_clone"
        self.original_html = '''
        <html>
        <head>
            <script src="http://example.com/foo.js?version=1.2"></script>
        </head>
        <body>
            <h1>Welcome to the Cloned Site</h1>
            <img src="http://example.com/images/logo.png?size=large" alt="Logo">
            <link rel="stylesheet" href="http://example.com/styles/main.css?v=3.4">
        </body>
        </html>
        '''

    def test_get_local_filename_with_query(self):
        url = "http://example.com/foo.js?version=1.2"
        local_path = "site_clone"
        local_filename = get_local_filename(url, local_path)
        expected_filename = "site_clone/foo.js"
        self.assertEqual(local_filename, expected_filename)
    
    def test_get_local_filename_with_multiple_query_parameters(self):
        url = "http://example.com/bar.css?name=value&other=param"
        local_path = "site_clone"
        local_filename = get_local_filename(url, local_path)
        expected_filename = "site_clone/bar.css"
        self.assertEqual(local_filename, expected_filename)
    
    def test_get_local_filename_without_query(self):
        url = "http://example.com/images/logo.png"
        local_path = "site_clone"
        local_filename = get_local_filename(url, local_path)
        expected_filename = "site_clone/images/logo.png"
        self.assertEqual(local_filename, expected_filename)

    def test_get_local_filename_no_filename(self):
        # Test case where URL does not have a filename
        url = 'http://example.com/path/'
        local_path = 'local_path'
        expected_local_filename = os.path.join(local_path, 'path', 'index.html')
        result = get_local_filename(url, local_path)
        self.assertEqual(result, expected_local_filename)
    
    def test_get_local_filename_with_querystring_no_filename(self):
        # Test case where URL has a querystring but no filename
        url = 'http://example.com/path/?query=string'
        local_path = 'local_path'
        expected_local_filename = os.path.join(local_path, 'path', 'index.html')
        result = get_local_filename(url, local_path)
        self.assertEqual(result, expected_local_filename)
    
    def test_get_local_filename_root_url(self):
        # Test case where URL is the root URL
        url = 'http://example.com/'
        local_path = 'site_clone'
        expected_local_filename = os.path.join(local_path, 'index.html')
        result = get_local_filename(url, local_path)
        self.assertEqual(result, expected_local_filename)
 
    def normalize_whitespace(self, text):
        return '\n'.join(line.strip() for line in text.strip().splitlines())
    
    def test_get_local_filename(self):
        url = "http://example.com/foo.js?version=1.2"
        local_filename = get_local_filename(url, self.local_path)
        expected_filename = "site_clone/foo.js"
        self.assertEqual(local_filename, expected_filename)
    
    def test_add_to_queue(self):
        content = '''
        <html>
        <head>
            <script src="http://example.com/foo.js"></script>
        </head>
        <body>
            <h1>Test Links</h1>
            <img src="http://example.com/images/logo.png" alt="Logo">
            <link rel="stylesheet" href="http://example.com/styles/main.css">
        </body>
        </html>
        '''
        to_visit = set()
        visited = set()
        
        def mock_add_to_queue(link):
            add_to_queue(link, to_visit, visited)
        
        extract_links(content, self.base_url, mock_add_to_queue)
        
        expected_to_visit = {
            'http://example.com/foo.js',
            'http://example.com/images/logo.png',
            'http://example.com/styles/main.css'
        }
        
        self.assertEqual(to_visit, expected_to_visit)

    def test_extract_links(self):
        content = '''
        <html>
        <head>
            <script src="http://example.com/foo.js"></script>
        </head>
        <body>
            <h1>Test Links</h1>
            <img src="http://example.com/images/logo.png" alt="Logo">
            <link rel="stylesheet" href="http://example.com/styles/main.css">
        </body>
        </html>
        '''
        base_url = "http://example.com"
        expected_links = {
            'http://example.com/foo.js',
            'http://example.com/images/logo.png',
            'http://example.com/styles/main.css'
        }

        found_links = set()

        def add_link_to_set(link):
            found_links.add(link)

        extract_links(content, base_url, add_link_to_set)

        self.assertEqual(found_links, expected_links)
 
    def test_update_links(self):
        html_with_mixed_links = '''
        <html>
        <head>
            <script src="http://example.com/foo.js"></script>
            <script>
                $("#id").html()
            </script>
        </head>
        <body>
            <h1>Welcome to the Cloned Site</h1>
            <img src="http://example.com/images/logo.png" alt="Logo">
            <link rel="stylesheet" href="http://example.com/styles/main.css">
        </body>
        </html>
        '''

        expected_html = '''
        <html>
        <head>
            <script src="/foo.js"></script>
            <script>
                $("#id").html()
            </script>
        </head>
        <body>
            <h1>Welcome to the Cloned Site</h1>
            <img src="/images/logo.png" alt="Logo">
            <link rel="stylesheet" href="/styles/main.css">
        </body>
        </html>
        '''

        updated_html = update_links(html_with_mixed_links, self.local_path, ["http://example.com/foo.js", "http://example.com/images/logo.png", "http://example.com/styles/main.css"])
        
        self.maxDiff = None  # Show full diff

        self.assertEqual(self.normalize_whitespace(updated_html), self.normalize_whitespace(expected_html))

    @patch('downloader.requests.Session.get')
    @patch('downloader.open', new_callable=mock_open)
    def test_download_file(self, mock_open_func, mock_get):
        # Set up the mock response
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.iter_content = lambda chunk_size: [b'test content']
        mock_response.__enter__.return_value = mock_response
        
        # Create a mock session
        session = create_tor_session()
        url = 'http://example.com/file.txt'
        local_filename = 'site_clone/file.txt'
        
        # Call the function to be tested
        result = download_file(session, url, local_filename)
        
        # Assertions
        self.assertTrue(result)
        mock_open_func.assert_called_once_with(local_filename, 'wb')
        handle = mock_open_func()
        handle.write.assert_called_once_with(b'test content') 

    @patch('downloader.requests.Session')
    @patch('downloader.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_download_site(self, mock_makedirs, mock_open_func, mock_session):
        def create_mock_response(url, **kwargs):
            mock_file_response = Mock()
            mock_file_response.status_code = 200
            mock_file_response.__enter__ = Mock(return_value=mock_file_response)
            mock_file_response.__exit__ = Mock(return_value=None)
            if url == "http://example.com/":
                mock_file_response.iter_content.return_value = [
                    b'<html><body>'
                    b'<script src="http://example.com/script.js"></script>'
                    b'<link href="http://example.com/style.css" rel="stylesheet">'
                    b'</body></html>'
                ]
            elif url == "http://example.com/script.js":
                mock_file_response.iter_content.return_value = [b'content of script.js']
            elif url == "http://example.com/style.css":
                mock_file_response.iter_content.return_value = [b'content of style.css']
            return mock_file_response

        # Setup initial conditions
        base_url = "http://example.com/"
        local_path = "local_path"

        # Mock the session's get method
        mock_session_instance = mock_session.return_value
        mock_get = mock_session_instance.get
        mock_get.side_effect = create_mock_response

        # Mock the file contents to read and write
        file_contents = {
            "local_path/index.html": '<html><body><script src="http://example.com/script.js"></script><link href="http://example.com/style.css" rel="stylesheet"></body></html>',
            "local_path/script.js": 'content of script.js',
            "local_path/style.css": 'content of style.css'
        }

        def mock_file_open(filename, mode, *args, **kwargs):
            if mode == 'r' and 'encoding' in kwargs:
                content = file_contents.get(filename, '')
                return mock_open(read_data=content).return_value
            elif mode == 'wb' or (mode == 'w' and 'encoding' in kwargs):
                return mock_open().return_value
            else:
                return mock_open().return_value

        mock_open_func.side_effect = mock_file_open

        # Call the download_site function
        download_site(base_url, local_path)

        # Expected file paths
        expected_index_path = os.path.join(local_path, "index.html")
        expected_script_path = os.path.join(local_path, "script.js")
        expected_style_path = os.path.join(local_path, "style.css")

        # Verify that os.makedirs was called to create directories
        mock_makedirs.assert_any_call(os.path.dirname(expected_index_path), exist_ok=True)
        mock_makedirs.assert_any_call(os.path.dirname(expected_script_path), exist_ok=True)
        mock_makedirs.assert_any_call(os.path.dirname(expected_style_path), exist_ok=True)

        # Verify that files were opened and written
        mock_open_func.assert_any_call(expected_index_path, 'wb')
        mock_open_func.assert_any_call(expected_script_path, 'wb')
        mock_open_func.assert_any_call(expected_style_path, 'wb')


if __name__ == "__main__":
    unittest.main()

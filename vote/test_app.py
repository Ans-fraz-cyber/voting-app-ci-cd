import unittest
from unittest.mock import patch, MagicMock
from app import app

class TestVoteApp(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('app.g')
    def test_home_page(self, mock_g):
        mock_redis = MagicMock()
        mock_g.redis = mock_redis
        
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Cats', response.data)
        self.assertIn(b'Dogs', response.data)
    
    @patch('app.g')
    def test_vote_post(self, mock_g):
        mock_redis = MagicMock()
        mock_g.redis = mock_redis
        
        response = self.app.post('/', data={'vote': 'a'})
        self.assertEqual(response.status_code, 200)
        mock_redis.rpush.assert_called_once()

if __name__ == '__main__':
    unittest.main()

import os
import flaskr
import unittest
import tempfile
import random
import string
import json

class FlaskrTestCase(unittest.TestCase):
	def setUp(self):
		flaskr.app.config['TESTING'] = True
		self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
		self.app = flaskr.app.test_client()

	def tearDown(self):
		os.close(self.db_fd)
		os.unlink(flaskr.app.config['DATABASE'])

	def test_get_key(self):
		rv = self.app.get('/key')
		jj = json.loads(rv.data.decode("utf8"))
		assert jj["response"]["error_code"] == 200
		
	def test_get_count(self):
		rv = self.app.get('/count')
		jj = json.loads(rv.data.decode("utf8"))
		assert jj["response"]["error_code"] == 200
		
	def test_get_info(self):
		for i in range(100):
			if random.random() < 0.2:
				key = "aa" + random.choice(string.ascii_letters) + random.choice(string.ascii_letters)
				rv = self.app.get('/info?key=%s' % key)
				jj = json.loads(rv.data.decode("utf8"))
				assert jj["response"]["error_code"] == 200
			elif random.random() < 0.4:
				key = "".join(random.choice(string.ascii_letters) for _ in range(3))
				rv = self.app.get('/info?key=%s' % key)
				jj = json.loads(rv.data.decode("utf8"))
				assert jj["response"]["error_code"] not in [200, 201]
			elif random.random() < 0.6:
				key = "".join(random.choice(string.ascii_letters) for _ in range(5))
				rv = self.app.get('/info?key=%s' % key)
				jj = json.loads(rv.data.decode("utf8"))
				assert jj["response"]["error_code"] not in [200, 201]
			else:
				key = ""
				rv = self.app.get('/info?key=%s' % key)
				jj = json.loads(rv.data.decode("utf8"))
				assert jj["response"]["error_code"] not in [200, 201]
		
	def test_get_expire(self):
		key = "aa" + random.choice(string.ascii_letters[:3]) + random.choice(string.ascii_letters)
		rv = self.app.get('/expire?key=%s' % key)
		jj = json.loads(rv.data.decode("utf8"))
		assert jj["response"]["error_code"] in [200, 201]
		
if __name__ == '__main__':
	unittest.main()

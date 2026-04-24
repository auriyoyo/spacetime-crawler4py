from scraper import is_valid
import unittest

class TestIsValid(unittest.TestCase):

    def test_normal_url_with_scheme(self):
        self.assertFalse(is_valid("httb://vision.ics.uci.edu/path;parameters?query=argument#fragment"))
        self.assertTrue(is_valid("http://vision.ics.uci.edu/path;parameters?query=argument#fragment"))
        self.assertTrue(is_valid("https://vision.ics.uci.edu/path;parameters?query=argument#fragment"))

    def test_four_domains_true(self):
        self.assertTrue(is_valid("https://vision.ics.uci.edu/path;parameters?query=argument#fragment"))
        self.assertTrue(is_valid("https://vision.cs.uci.edu/path;parameters?query=argument#fragment"))
        self.assertTrue(is_valid("http://vision.informatics.uci.edu/path;parameters?query=argument#fragment"))
        self.assertTrue(is_valid("http://vision.stat.uci.edu/path;parameters?query=argument#fragment"))

    def test_outside_of_four_domains_false(self):
        self.assertFalse(is_valid("https://alexa.uci.edu/path;parameters?query=argument#fragment"))
        self.assertFalse(is_valid("https://bio.uci.edu/path;parameters?query=argument#fragment"))
        self.assertFalse(is_valid("https://stat.uci.edu/path;parameters?query=argument#fragment"))
        self.assertFalse(is_valid("https://hi.informatics.uci.edu.pi/path;parameters?query=argument#fragment"))

    def test_non_websites_false(self):
        self.assertFalse(is_valid("https://vision.ics.uci.edu/path.pdf"))
        self.assertFalse(is_valid("https://vision.ics.uci.edu/hello.exe"))
        self.assertFalse(is_valid("https://vision.informatics.uci.edu/vid.mp3"))




if __name__ == '__main__':
    unittest.main()

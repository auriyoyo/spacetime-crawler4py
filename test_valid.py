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

    def test_wont_go_to_dataset_page(self):
        self.assertFalse(is_valid("https://archive.ics.uci.edu/datasets/"))
        self.assertFalse(is_valid("https://archive.ics.uci.edu/dataset/2/adult"))
        self.assertFalse(is_valid("https://archive.ics.uci.edu/dataset/59/letter+recognition"))
        self.assertFalse(is_valid("https://archive.ics.uci.edu/ml/datasets/Letter+recognition"))

    def test_wont_go_to_urls_marked_with_events_or_as_calendar(self):
        self.assertFalse(is_valid("https://ics.uci.edu/events/"))
        self.assertFalse(is_valid("https://ics.uci.edu/events/month/?tribe__ecp_custom_47%5B0%5D=Career+Development"))
        self.assertFalse(is_valid("https://stat.ics.uci.edu/calendar/"))




if __name__ == '__main__':
    unittest.main()

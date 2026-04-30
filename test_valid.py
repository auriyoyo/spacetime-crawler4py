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

    def test_wont_go_to_page_with_do_equals_media(self):
        self.assertFalse(is_valid("https://wiki.ics.uci.edu/doku.php/projects:start?tab_details=history&do=media&tab_files=upload&image=security%3Apasted%3A20250905-094915.png&ns=services%3Asun_grid_engine"))
        self.assertFalse(is_valid("https://wiki.ics.uci.edu/doku.php/projects:start?tab_files=files&do=media&tab_details=view&image=vpn_settings5.png&ns=security"))
        self.assertFalse(is_valid("https://wiki.ics.uci.edu/doku.php/projects:start?tab_files=search&do=media&tab_details=view&image=security%3Avpn_settings3.png&ns=services%3Adatabase"))
        self.assertFalse(is_valid("https://intranet.ics.uci.edu/doku.php/sidebar?tab_details=history&do=media&tab_files=search&image=pasted%3A20250808-1801032.png&ns=pasted"))
        self.assertFalse(is_valid("http://intranet.ics.uci.edu/doku.php/login?tab_details=view&do=media&tab_files=files&image=pasted%3A20250808-1801032.png&ns=pasted"))

    def test_wont_go_to_pages_with_copying_editing_exporting_or_difference(self):
        self.assertTrue(is_valid("http://intranet.ics.uci.edu/doku.php/login:login"))
        self.assertFalse(is_valid("http://swiki.ics.uci.edu/doku.php/software:windows10_eol?do=edit"))
        self.assertFalse(is_valid("http://swiki.ics.uci.edu/doku.php/sidebar?do="))
        self.assertFalse(is_valid("http://swiki.ics.uci.edu/doku.php/accounts:new_user_guide?do=export_pdf"))
        self.assertFalse(is_valid("http://intranet.ics.uci.edu/doku.php/start?do=diff&rev2%5B0%5D=1587997204&rev2%5B1%5D=1767734819&difftype=sidebyside"))

    def test_wiki_query_traps(self):
        # idx pages
        self.assertFalse(is_valid("https://wiki.ics.uci.edu/doku.php/wiki:nonexisting?idx=wiki"))
        self.assertFalse(is_valid("http://swiki.ics.uci.edu/doku.php/storage:onedrive?idx=storage"))
        self.assertFalse(is_valid("http://swiki.ics.uci.edu/doku.php/security:zotdefend?idx=services%3Adatabase"))

        # login/index actions create alternate wiki views
        self.assertFalse(is_valid("http://swiki.ics.uci.edu/doku.php/services:network?do=login&sectok="))
        self.assertFalse(is_valid("http://swiki.ics.uci.edu/doku.php/services:network?do=index"))
        self.assertFalse(is_valid("https://wiki.ics.uci.edu/doku.php/accounts:start?do=recent"))
        self.assertFalse(is_valid("https://wiki.ics.uci.edu/doku.php/accounts:start?do=backlink"))
        self.assertFalse(is_valid("https://wiki.ics.uci.edu/doku.php/accounts:start?do=revisions"))
        self.assertFalse(is_valid("https://wiki.ics.uci.edu/doku.php/accounts:start?do=diff"))

        # revision/history comparison pages
        self.assertFalse(is_valid("https://wiki.ics.uci.edu/doku.php/accounts:fuse-sshfs?rev=1455843173"))
        self.assertFalse(is_valid("https://wiki.ics.uci.edu/doku.php/accounts:fuse-sshfs?rev=1455843173&do=diff"))
        self.assertFalse(is_valid("https://wiki.ics.uci.edu/doku.php/accounts:fuse-sshfs?do=diff&rev2%5B0%5D=1455842164&rev2%5B1%5D=1776270938&difftype=sidebyside"))

        # normal wiki content page should still be allowed
        self.assertTrue(is_valid("http://swiki.ics.uci.edu/doku.php/services:network"))

    # have to run these later
    def test_wont_go_to_diff_comparison_page(self):
        self.assertFalse(is_valid("https://ics.uci.edu/wiki/public/wiki/cs122b-2017-winter-project3?action=diff&version=5"))
        self.assertFalse(is_valid("https://ics.uci.edu/wiki/public/wiki/cs122b-2017-winter-project4?action=diff&version=2"))

    def test_wont_go_to_grape_ics_uci_edu_pages(self):
        self.assertFalse(is_valid("https://grape.ics.uci.edu/wiki/public/wiki/cs122b-2017-winter-project4?format=txt&version=11"))
        self.assertFalse(is_valid("https://grape.ics.uci.edu/wiki/public/wiki/cs122b-2016-spring-project5-mysql-master-slave?action=history"))

    def test_wont_go_to_txt_files(self):
        self.assertFalse(is_valid("http://seal.ics.uci.edu/projects/covert/appList.txt"))
        self.assertFalse(is_valid("https://ics.uci.edu/wiki/public/wiki/cs122b-2017-winter-project3?format=txt&version=8"))



if __name__ == '__main__':
    unittest.main()

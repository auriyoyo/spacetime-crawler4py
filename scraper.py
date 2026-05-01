import re
from urllib.parse import urlparse, urljoin, urlunparse, unquote
from analytics import (
    tokenize,
    update_longest_page,
    update_word_counts,
    update_subdomain_dict,
    get_unique_subdomain_with_unique_pages,
    STOP_WORDS,
    save_all,
    load_word_counts,
    save_and_calc_avg_page_size,
)
from bs4 import BeautifulSoup

load_word_counts()
pages_crawled = 0
sum_bytes = 0
byte_pages = 0


def scraper(url, resp):
    global pages_crawled
    global sum_bytes
    global byte_pages

    # If error is that the content is too large, save its url and size to a text file for inspection
    if resp.status == 607:
        with open("too_large.txt", "a") as f:
            f.write(f"{url}")

    # check for valid response, return empty list if not valid.
    if resp.status != 200 or not resp.raw_response or not resp.raw_response.content:
        if resp.error:
            print(f"Error crawling {url}: {resp.error}")
        return []

    soup = BeautifulSoup(resp.raw_response.content, "lxml")
    # extract text from relevant tags and target main content only
    text = " ".join(
        tag.get_text()
        for tag in soup.find_all(
            [
                "p",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
                "li",
                "td",
                "th",
                "article",
                "section",
                "main",
            ]
        )
    )

    # tokenize the text and filter out stop words and numeric tokens
    words = []
    all_words = tokenize(text)

    # only consider pages with at least 50 words to avoid low-information pages
    if len(all_words) < 50:
        return []

    for w in all_words:
        w = w.lower()
        if w not in STOP_WORDS and not w.isnumeric():
            words.append(w)

    # update word counts and longest page info
    update_word_counts(words)
    update_longest_page(url, len(words))

    # update sum_bytes with the number of bytes in this page
    if "content-length" in resp.raw_response.headers:
        length = resp.raw_response.headers["content-length"]
        sum_bytes += int(length)
        byte_pages += 1

    # increment pages_crawled and save info every 100 pages
    pages_crawled += 1
    if pages_crawled % 100 == 0:
        save_all()
        save_and_calc_avg_page_size(sum_bytes, byte_pages)
    links = extract_next_links(url, resp)
    valid_next_links = [
        link
        for link in links
        if is_valid(link)
        and (
            "content-length" not in resp.raw_response.headers
            or int(resp.raw_response.headers["content-length"]) < 100000
        )
    ]

    # grab subdomain (no protocol) and unique pages within that domain
    parsed = urlparse(url)
    update_subdomain_dict(f"{parsed.netloc}", valid_next_links)

    return valid_next_links


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # 1. Check if the response is actually valid before trying to extract links
    if resp.status != 200 or not resp.raw_response or not resp.raw_response.content:
        # If the status is not 200, print the error message to allow error checking on our side.
        if resp.error:
            print(f"Error crawling {url}: {resp.error}")
        return []

    # 1B. Check if the content type is HTML before trying to parse it
    content_type = resp.raw_response.headers.get("Content-Type", "")
    if "text/html" not in content_type:
        return []

    # 2. Parse the HTML content and extract links using BeautifulSoup
    soup = BeautifulSoup(resp.raw_response.content, "lxml")
    links = []

    for tag in soup.find_all("a", href=True):
        href = tag["href"]

        # 3. Convert relative URLs to absolute URLs
        # 3B. Using try-catch to prevent urljoin from crashing on malformed hrefs
        try:
            absolute = urljoin(url, href)
            # 4. Strip the fragment identifier (the part after '#') from the URL
            parsed = urlparse(absolute)
            defragmented = urlunparse(parsed._replace(fragment=""))
            links.append(defragmented)
        except ValueError:
            # if a ValueError occurs, skip the link and continue the crawling process
            continue

    # 5. Return the list of links
    return links


def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # Invalid if the netloc (sub/domain) doesn't contain any of the four valid ones
        if not any(
            parsed.netloc.endswith(domain)
            for domain in [
                ".ics.uci.edu",
                ".cs.uci.edu",
                ".informatics.uci.edu",
                ".stat.uci.edu",
            ]
        ):
            return False

        # Avoiding large files with low information value
        for ml_dataset in ["/datasets/", "/dataset/", "/ml/"]:
            if parsed.path.startswith(ml_dataset):
                return False

        # Avoiding calendars
        if parsed.path.startswith("/events/") or parsed.path.startswith("/calendar/"):
            return False

        # Using unquote to decode URL-encoded characters enabling proper detection of invalid query parameters
        query = unquote(parsed.query).lower()

        # Avoid DokuWiki tab pages, pages with dropdowns, directories
        if "idx=" in query:
            return False
        if parsed.netloc == "dale-cooper-v0.ics.uci.edu":
            return False
        if re.match(".*C=[A-Z];O=[A-Z]", parsed.query):
            return False

        # Avoid sitemap pages with low info
        if "sitemap" in parsed.path.lower():
            return False

        # Avoiding media manager websites (low info, gets trapped between all the buttons)
        # Avoid DokuWiki action pages
        if "do=" in query:
            return False

        # Avoid excessive query parameter combinations
        if query.count("=") > 3:
            return False

        # Avoid long noisy queries
        if len(query) > 60:
            return False

        # Avoid old revision/version-history pages
        if any(x in query for x in ["rev=", "rev2", "difftype", "action=diff"]):
            return False

        # Avoid pages with pagination in the path which can lead to infinite crawling of similar pages
        if re.search(r"/page/\d+", parsed.path):
            return False

        # Avoid author pages which often have low information value and can lead to crawling many similar pages
        if re.search(r"/author/", parsed.path):
            return False

        # Avoid links that trigger download of files or pdfs
        if any(
            x in query
            for x in [
                "action=raw",
                "action=download",
                "format=pdf",
                "output=pdf",
                "export_pdf",
                "format=txt",
            ]
        ):
            return False

        # Avoid certain trap websites
        if parsed.netloc == "grape.ics.uci.edu":
            return False

        # Avoid patterns of login-blocked pages
        if parsed.netloc == "intranet.ics.uci.edu" and ":start" in parsed.path:
            return False
        if "/login" in parsed.path:
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|mpg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv|txt"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            + r"|flv|webm|bib|sql|db|sqlite"
            + r"|mat|rdata|rds|java|py|cpp|c|h"
            + r"|ppsx|pps|key|fig|sketch|ai|svg)$",
            parsed.path.lower(),
        )


    except TypeError:
        print("TypeError for ", parsed)
        raise

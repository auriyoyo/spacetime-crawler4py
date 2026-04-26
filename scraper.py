import re
from urllib.parse import urlparse, urljoin, urlunparse
from analytics import (
    tokenize,
    update_longest_page,
    update_word_counts,
    update_subdomain_dict,
    get_unique_subdomain_with_unique_pages,
    STOP_WORDS,
    save_all,
    load_word_counts,
)
from bs4 import BeautifulSoup

load_word_counts()
pages_crawled = 0

def scraper(url, resp):
    global pages_crawled

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
    for w in all_words:
        w = w.lower()
        if w not in STOP_WORDS and not w.isnumeric():
            words.append(w)

    # update word counts and longest page info
    update_word_counts(words)
    update_longest_page(url, len(words))
    
    # increment pages_crawled and save info every 100 pages
    pages_crawled += 1
    if pages_crawled % 100 == 0:
        save_all()
    links = extract_next_links(url, resp)
    valid_next_links = [link for link in links if is_valid(link)]

    # grab subdomain (no protocol) and unique pages within that domain
    parsed = urlparse(url)
    update_subdomain_dict(f"{parsed.netloc}", len(valid_next_links))
        
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

    # 2. Parse the HTML content and extract links using BeautifulSoup
    soup = BeautifulSoup(resp.raw_response.content, "lxml")
    links = []

    for tag in soup.find_all("a", href=True):
        href = tag["href"]

        # 3. Convert relative URLs to absolute URLs
        absolute = urljoin(url, href)

        # 4. Strip the fragment identifier (the part after '#') from the URL
        parsed = urlparse(absolute)
        defragmented = urlunparse(parsed._replace(fragment=""))

        links.append(defragmented)
    
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
        # ASSUMING period is required, gonna ask 4/24
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

        # Avoiding infinite traps
        if parsed.path.startswith("/events/") or parsed.path.startswith("/calendar/"):
            return False
            # can also check if it ends with a date if necessary, but seems to always start with /events/

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$",
            parsed.path.lower(),
        )

    except TypeError:
        print("TypeError for ", parsed)
        raise

import html2text
import re
import urllib.request as url_request


def url2text(url, ignore_links=False):
    """ Reads a url and transforms it to string.

    Parameters
    -------
    urls : str
        HTML URL that is going to be downloaded.
    ignore_links : bool
        Whether to ignore links or not.

    Returns
    -------
    html : str
        Downloaded html as string.
    """

    h = html2text.HTML2Text()
    h.ignore_links = ignore_links

    with url_request.urlopen(url) as f:
        html = f.read().decode('utf-8')

        html = h.handle(html)

    return html


def get_all_urls(url, web_page, include_http=True):
    """ Reads an URL and find all the links inside it.

    Parameters
    -------
    url : str
        HTML URL that contains multiple URLs as links.
    web_page : str
        Base URL page (we keep only links to this page)
    include_http: bool
        Whether the pattern has http(s):// or not.

    Returns
    -------
    urls : list<str>
        List of urls.
    """
    pattern = ''

    if include_http:
        pattern = 'http[s]*://'

    pattern += web_page.replace('.', '[.]') + '.+'

    text = url2text(url, ignore_links=False)
    urls = re.findall(pattern, text)

    return urls


def get_all_urls_list(url, web_page, include_http=True, next_button_html=None):
    """ Reads an URL and find all the links inside it with a Next button.

    This function supposes that the url has a list of urls that is splitted in
    several pages that can be changed using the previous/next buttons.

    Parameters
    -------
    url : str
        HTML URL that contains multiple URLs as links.
    web_page : str
        Base URL page (we keep only links to this page).
    include_http: bool
        Whether the pattern has http(s):// or not.
    next_button_html : str
        Text that is written in the html for the button.

    Returns
    -------
    urls : list<str>
        List of urls.
    """
    urls = get_all_urls(url, web_page, include_http=include_http)

    # See if there is a next button in the page
    text = url2text(url, ignore_links=False)

    if next_button_html is None:
        return urls

    idx = text.find(next_button_html)

    # If there is a next button we have to load the next page as well
    if idx >= 0:
        # The urls are between brackets
        text = text[(idx + len(next_button_html) + 1):]
        last_char = text.find(')')
        # For some weird reason some links have a \n inside it
        next_url = text[:last_char].replace('\n', '')

        urls += get_all_urls_list(next_url, web_page,
                                  include_http, next_button_html)

    return urls

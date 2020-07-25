import re
from tqdm import tqdm

from utils import url2text, get_all_urls, get_all_urls_list


class SuperHeroDataProcessor():
    POWER_ABILITIES_SECTION = '## Powers and Abilities'
    POWER_SECTION = '### Powers'
    ABILITIES_SECTION = '### Abilities'
    POWERS_PATTERN = '[*] [*][*].+:[*][*]'
    MARVEL_BASE_PAGE = 'https://marvel.fandom.com/'
    """ Class that extracts information from Marvel
        Fandom webpages.


    Parameters
    -------
    urls : list<string>
        HTML URLs that are going to be downloaded.
    all_characters : boolean
        If true saves in urls attribute all the urls from
        https://marvel.fandom.com/wiki/Category:Characters.
    """

    def __init__(self, urls=None, all_characters=False):
        self.urls = urls
        if all_characters:
            self.urls = SuperHeroDataProcessor._get_all_character_urls()

    @classmethod
    def _get_all_character_urls(cls):

        marvel_character_page = SuperHeroDataProcessor.MARVEL_BASE_PAGE + 'wiki/Category:Characters'

        # The list of urls is filter by character first letter
        urls = get_all_urls(marvel_character_page, 'marvel.fandom.com', include_http=True)
        urls = [url for url in urls if 'Category:Characters&from' in url]

        # There is a problem with some links (they have some special character
        # at the end separated by a whitespace)
        urls = [url.split(' ')[0] for url in urls]

        all_urls = set()

        for url in tqdm(urls):
            character_urls = get_all_urls_list(url, web_page='wiki/',
                                               include_http=False,
                                               next_button_html='[ Next\n]')
            character_urls = [SuperHeroDataProcessor.MARVEL_BASE_PAGE
                              + url.split('"')[0].replace('\\', '').strip()
                              for url in character_urls if '"' in url]
            all_urls = all_urls.union(character_urls)

        return list(all_urls)

    def load_data(self):
        """ Gets the information that it is needed from the htmls.

        Returns
        -------
        texts_transformed : dict<string><string>
            Dictionary where keys are the url and the value
            is a list of strings with the information.

        """
        texts = url2text(self.urls, ignore_links=True)

        text_transformed = {}

        for url, text in texts.items():
            text = self.get_powers_text(text)
            powers = self.extract_powers(text)

            # Get the name of the character
            name = url.split('/')[-1].replace('_', ' ')

            text_transformed[url] = [name, powers]

        return text_transformed

    def extract_powers(self, text):
        """ Gets from the powers section a list of super powers.

        Parameters
        -------
        text : string
            Power section.

        Returns
        -------
        list<string>
            List of super powers.

        """
        texts = re.findall(self.POWERS_PATTERN, text)
        # Remove undesired characters
        texts = [t.lower().replace('*', '').replace('-', ' ').strip() for t in texts]

        return texts

    def get_powers_text(self, text):
        """ Gets from the text only the powers section.

        Parameters
        -------
        text : string
            All the HTML transformed to string.

        Returns
        -------
        string
            Text with only the powers section.

        """
        idx = text.find(self.POWER_ABILITIES_SECTION)
        text = text[idx:]
        start = text.find(self.POWER_SECTION)
        end = text.find(self.ABILITIES_SECTION)

        return text[start:end]

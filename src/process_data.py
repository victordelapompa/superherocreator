from tqdm import tqdm

from superhero import SuperHero
from utils import url2text, get_all_urls, get_all_urls_list


class SuperHeroDataExtractor():
    MARVEL_BASE_PAGE = 'https://marvel.fandom.com/'
    """ Class that extracts information from Marvel Fandom webpages.

    Parameters
    -------
    urls : list<str>
        HTML URLs that are going to be downloaded.
    all_characters : bool
        If true saves in urls attribute all the urls from
        https://marvel.fandom.com/wiki/Category:Characters.
    """

    def __init__(self, urls=None, all_characters=False):
        self.urls = urls
        if all_characters:
            self.urls = SuperHeroDataExtractor._get_all_character_urls()

    @classmethod
    def _get_all_character_urls(cls):

        marvel_character_page = SuperHeroDataExtractor.MARVEL_BASE_PAGE + 'wiki/Category:Characters'

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
            character_urls = [SuperHeroDataExtractor.MARVEL_BASE_PAGE
                              + url.split('"')[0].replace('\\', '').strip()
                              for url in character_urls if '"' in url]
            all_urls = all_urls.union(character_urls)

        return list(all_urls)

    @classmethod
    def _load_url(cls, url):
        try:
            texturl = url.split('wiki')[1].replace('/', '').replace('*', '')
            file_path = '../data/raw_hero/' + texturl + '.txt'

            with open(file_path, 'rb') as f:
                text = f.read().decode('utf-8')
        # If file does not exist, we have to load the HTML
        except IOError:
            print(url)
            text = url2text(url, ignore_links=True)

        return text

    def save_urls_content(self):
        """ Loads all the HTML in all the urls and saves them in data folder.
        """
        for url in tqdm(self.urls):
            text = url2text(url, ignore_links=True)
            texturl = url.split('wiki')[1].replace('/', '').replace('*', '')
            file_path = '../data/raw_hero/' + texturl + '.txt'
            with open(file_path, 'wb') as f:
                f.write(text.encode('utf-8'))

    def load_data(self):
        """ Gets the information that it is needed from the htmls.

        Parameters
        -------
        save_texts : bool
            Whether to save or not html texts.

        Returns
        -------
        texts_transformed : list<list>
            List where every element has information form one URL.
        columns: list<str>
            List of the name of every column.
        """
        text_transformed = []

        for url in tqdm(self.urls):
            try:
                text = SuperHeroDataExtractor._load_url(url)
            except Exception:
                print('Not found:', url)
            sh = SuperHero(url, text)
            powers = sh.powers

            gallery_info = sh.get_gallery_information()

            # Get the name of the character
            name = url.split('/')[-1].replace('_', ' ')

            text_transformed.append([url, name, powers, *gallery_info])

        columns = ['url', 'name', 'powers', *(SuperHero.GALLERY_PRETTY_FIELDS)]

        return text_transformed, columns

import re


class SuperHero():
    POWERS_PATTERN = '[*] [*][*].+:[*][*]'
    POWER_ABILITIES_SECTION = '## Powers and Abilities'
    POWER_SECTION = '### Powers'
    ABILITIES_SECTION = '### Abilities'
    START_GALLERY_SECTION = 'Gallery'
    END_GALLERY_SECTION = '## History'
    GALLERY_RAW_FIELDS = ['Real Name', 'Current\nAlias\n', 'Aliases', 'Affiliation', 'Identity',
                          'Citizenship', 'Occupation', 'Gender', 'Height', 'Weight',
                          'Eyes', 'Hair', 'Origin', 'Universe', 'Creators']
    GALLERY_PRETTY_FIELDS = ['Real Name', 'Current Alias', 'Aliases', 'Affiliation', 'Identity',
                             'Citizenship', 'Occupation', 'Gender', 'Height', 'Weight',
                             'Eyes', 'Hair', 'Origin', 'Universe', 'Creators']
    """ Class that has information from one superhero.

    Attributes
    -------
    gallery_info : dict<str><str>
        Dictionary where key is the field name and the value
        is the value of that hero in that field.

    Parameters
    -------
    url : str
        URL with the information of the superhero.
    html : str
        HTML of the superhero.
    """
    def __init__(self, url, html):
        self.url = url
        self.html = html
        self.gallery_info = None

    @classmethod
    def _get_text_between_two_strings(cls, text, start_string, end_string):
        start = text.find(start_string)
        text = text[start:]
        end = text.find(end_string)

        return text[:end]

    @property
    def powers(self):
        """ List of super powers.
        """
        texts = re.findall(SuperHero.POWERS_PATTERN, self.get_powers_text())
        # Remove undesired characters
        texts = [t.lower()
                  .replace('*', '')
                  .replace('-', ' ')
                  .replace(':', '')
                  .strip()
                 for t in texts]

        return texts

    def get_gallery_information(self):
        """ Gets from the gallery section some information.

        Returns
        -------
        list<str>
            List with the information.
        """
        gallery_info = []
        gallery_text = SuperHero._get_text_between_two_strings(self.html,
                                                               SuperHero.START_GALLERY_SECTION,
                                                               SuperHero.END_GALLERY_SECTION)
        regex_number_brackets = re.compile(r'\[[0-9]+\]', re.IGNORECASE)
        regex_multiple_spaces = re.compile(r' [ ]+', re.IGNORECASE)
        for field_name in SuperHero.GALLERY_RAW_FIELDS:
            # Every section seems to have a '###' at the end
            value = SuperHero._get_text_between_two_strings(gallery_text,
                                                            ') ' + field_name,
                                                            '###')

            # Delete the field_name from the value returned
            value = value.replace(') ' + field_name, '')
            # Delete special characters
            value = value.replace('\n', '') \
                         .replace('_', ' ') \
                         .replace('-', ' ')
            # Delete numbers between [ ], and remove multiple spaces
            value = regex_number_brackets.sub('', value)
            value = regex_multiple_spaces.sub(' ', value)
            gallery_info.append(value.strip())

        self.gallery_info = dict(zip(SuperHero.GALLERY_PRETTY_FIELDS, gallery_info))

        return gallery_info

    def get_powers_text(self):
        """ Gets the powers section from the html text.

        Returns
        -------
        text : str
            Text with only the powers section.

        """
        idx = self.html.find(SuperHero.POWER_ABILITIES_SECTION)
        text = self.html[idx:]
        text = SuperHero._get_text_between_two_strings(text,
                                                       SuperHero.POWER_SECTION,
                                                       SuperHero.ABILITIES_SECTION)

        # If there was no Ability subsection we have to search for a ##
        if SuperHero.ABILITIES_SECTION not in self.html:
            text = SuperHero._get_text_between_two_strings(text,
                                                           SuperHero.POWER_SECTION,
                                                           '##')
        return text

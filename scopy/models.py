
class ScopusRef(object):
    def __init__(self, json):
        self.authors = []
        self.title = None
        self.volume = None
        self.issue = None
        self.date = None
        self.pages = None
        self.publication = None

        self._populate_fields(json)

    def __repr__(self):
        return u'' \
            'authors: %s\n' % self.authors + \
            'title: %s\n' % self.title + \
            'volume: %s\n' % self.volume + \
            'issue: %s\n' % self.issue + \
            'date: %s\n' % self.date + \
            'pages: %s\n' % self.pages + \
            'publication: %s\n' % self.publication

    def _populate_fields(self, json):
        info = json.get('ref-info')

        # Descend through author JSON tree
        next_level = info
        x = 0
        author_levels = ['ref-authors', 'author']
        while next_level is not None and x < len(author_levels):
            next_level = next_level.get(author_levels[x])
            x += 1

        # The above returns a list of authors.
        # Iterate through and add the names to self.authors
        if next_level is not None:
            if not isinstance(next_level, dict):
                for author in next_level:
                    if 'ce:indexed-name' in author.keys():
                        self.authors.append(author.get('ce:indexed-name'))
                    elif ('ce:surname', 'ce:initials') in author.keys():
                        name = ' '.join([author['ce:surname'], author['ce:initials']])
                        self.authors.append(name)
            else:
                if 'ce:indexed-name' in next_level.keys():
                    self.authors.append(next_level.get('ce:indexed-name'))
                elif ('ce:surname', 'ce:initials') in next_level.keys():
                    name = ' '.join([next_level['ce:surname'], next_level['ce:initials']])
                    self.authors.append(name)

        # Get page ranges
        next_level = info
        x = 0
        page_levels = ['ref-volisspag', 'pagerange']
        while next_level is not None and x < len(page_levels):
            next_level = next_level.get(page_levels[x])
            x += 1

        if next_level is not None:
            if ('@first', '@last') in next_level.keys():
                self.pages = '-'.join([next_level['@first'], next_level['@last']])

        # Get issue and volume:
        voliss = info.get('voliss')
        if voliss is not None:
            self.issue = voliss.get('@issue')
            self.volume = voliss.get('@volume')

        # Get publication year
        pubyear = info.get('ref-publicationyear')
        if pubyear is not None:
            self.date = pubyear.get('@first')

        # Get title
        title = info.get('ref-title')
        if title is not None:
            self.title = title.get('ref-titletext')

        # Get publication
        self.publication = info.get('ref-sourcetitle')


class ScopusEntry(object):
    def __init__(self, json):
        self.doi = None
        self.eid = None
        self.pii = None
        self.title = None
        self.publisher = None
        self.type = None
        self.issn = None
        self.volume = None
        self.issue = None
        self.pages = None
        self.date = None
        self.authors = []
        self.abstract = None
        self.link = None
        self.article = None

        self._populate_fields(json)

    def _populate_fields(self, json):
        coredata = json.get('coredata')

        self.doi = coredata.get('prism:doi')
        self.eid = coredata.get('eid')
        self.pii = coredata.get('pii')
        self.title = coredata.get('dc:title')
        self.publisher = coredata.get('prism:publicationName')
        self.type = coredata.get('prism:aggregationType')
        self.issn = coredata.get('prism:issn')
        self.volume = coredata.get('prism:volume')
        self.issue = coredata.get('prism:issueIdentifier')
        self.pages = coredata.get('prism:pageRange')
        self.date = coredata.get('prism:coverDate')
        self.abstract = coredata.get('dc:description')

        # Get authors
        author_section = coredata.get('dc:creator')
        if author_section is not None:
            if isinstance(author_section, list):
                for author in author_section:
                    name = author.get('$')
                    if name is not None:
                        self.authors.append(name)
            else:
                name = author_section.get('$')
                if name is not None:
                    self.authors.append(name)

        # Get article links
        links = coredata.get('link')
        if isinstance(links, list):
            self.link = []
            for item in links:
                link = item.get('@href')
                if link is not None:
                    self.link.append(link)
        else:
            link = links.get('@href')
            if link is not None:
                self.link = link

        # Get article (if returned in JSON)
        article_text = json.get('originalText')
        if isinstance(article_text, dict):
            self.article = ''
        else:
            self.article = article_text

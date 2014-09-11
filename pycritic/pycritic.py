import requests
import bs4

# It's "seems" a good idea to use this "enum", for now
class Category(object):
    ALL = 0
    MOVIE = 1
    GAME = 2
    ALBUM = 3
    TV = 4
    PERSON = 5
    TRAILER = 6
    COMPANY = 7

# Contains info about the query to be made
class Query(object):
    # Standard constructor (w/ parameters)
    def __init__(self, category, terms):
        self.browser = Browser()
        self.response = ""
        self.soup = ""
        self.category = category
        self.terms = terms
        self.search_term=self.build_terms(self.terms)
        self.base_url = "http://www.metacritic.com/search/"
        partial_url = {Category.ALL: self.base_url + "all",
                       Category.MOVIE: self.base_url + "movie",
                       Category.GAME: self.base_url + "game",
                       Category.ALBUM: self.base_url + "album",
                       Category.TV: self.base_url + "tv",
                       Category.PERSON: self.base_url + "person",
                       Category.TRAILER: self.base_url + "trailer",
                       Category.COMPANY: self.base_url + "company"}[self.category]
        self.search_url = partial_url + "/" + self.search_term + "/results"

    # Returns the URL of the created query
    def get_url(self):
        return self.search_url

    def build_terms(self,term):
        search_string = ''.join(c for c in term if c.isalnum() or c.isspace())
        search_string=search_string.replace(" ","%20")
        return search_string

    def get(self):
        self.response = self.browser.get(self.search_url)
        self.soup = bs4.BeautifulSoup(self.response.content)
        return self.extract_data()

    def extract_data(self):
        table = self.soup.find("ul", {"class" : "search_results module"})
        if table is None:
            return None  #Returns None in case there are no search results
        urls=[]
        for row in table.findAll("div",{"class":"main_stats"}):
            urls.append(self._extract_url(row))
        return urls
        #return resource

    def _extract_url(self,row):
        url = row.find("h3",{"class":"product_title basic_stat"})
        return "http://www.metacritic.com"+url.a.get('href')


# This class represents a generic resource found at Metacritic
class Resource(object):
    def __init__(self, name, date, category, metascore, userscore, description,platform):
        self.name = name
        self.date = date
        self.category = category
        self.metascore = metascore
        self.userscore = userscore
        self.description = description
        self.platform = platform

class Response(object):
    def __init__(self, status, content):
        self.status = status
        self.content = content

    def valid(self):
        return (self.status == 200)


class Browser(object):
    def get(self, url):
        # Modify User Agent as per convenience
        user_agent = {'User-agent': 'Mozilla/5.0'}
        request = requests.get(url, headers = user_agent)
        response = Response(request.status_code, request.content)
        return response


class Scraper(object):
    def __init__(self):
        self.browser = Browser()
        self.response = ""
        self.soup = ""

    def get(self, url):
        self.response = self.browser.get(url)
        self.soup = bs4.BeautifulSoup(self.response.content)
        return self.extract_data()

    def extract_data(self):
        name = self._extract_name()
        date = self._extract_date()
        category = self._extract_category()
        metascore = self._extract_metascore()
        userscore = self._extract_userscore()
        description = self._extract_description()
        platform=self._extract_platform()
        resource = Resource(name, date, category, metascore, userscore, description,platform)
        return resource

    def _extract_name(self):
        titles = self.soup.find("span", {"itemprop":"name"})
        if titles is None:
            return None
        name = titles.string.strip()
        return name

    def _extract_date(self):
        dates = self.soup.select(".release_data")
        if dates is None:
            return None
        date = dates[0].select(".data")[0].text.strip()
        return date

    def _extract_category(self):
        # TODO
        return Category.GAME

    def _extract_platform(self):
        platfrom=self.soup.find("span", {"itemprop":"device"})
        if platfrom is None:
            return None
        return platfrom.string.strip()

    def _extract_metascore(self):
        score = self.soup.find("span", {"itemprop":"ratingValue"})
        if score is None:
            return None
        return score.string

    def _extract_userscore(self):
        score=self.soup.find("div",{"class":"metascore_w user large game mixed"})
        if score is None:
            return None
        return score.string

    def _extract_description(self):
        section = self.soup.find("span",{"itemprop":"description"})
        if section is None:
            return str(None)
        description=""
        collapsed = section.find("span",{"class":"blurb blurb_collapsed"})
        if collapsed is None:
            description=unicode(section.span.string)
        else:
            expanded = section.find("span",{"class":"blurb blurb_expanded"})
            description = unicode(collapsed.string+expanded.string)
        return unicode(description)
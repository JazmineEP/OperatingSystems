import requests
import bs4


def print_resource_data(resource):
    print("Name: " + resource.name)
    print("Metascore: " + str(resource.metascore))

def how_long_beat():
    results_list = HowLongToBeat().search("gears")
    if results_list is not None and len(results_list) > 0:
        best_element = max(results_list, key=lambda element: element.similarity)
        #print(format_result(best_element.gameplay_completionist)+" "+best_element.gameplay_completionist_unit)
        return(format_result(best_element.gameplay_completionist)+" "+best_element.gameplay_completionist_unit)
def format_result(time_to_beat):
    half_index = time_to_beat.find('½')               # Retorna el índice donde se encuentra el caracter '½'
    if half_index != -1:                              # Si el caracter '½' existe en el string...
        return time_to_beat[0:half_index] + '.30'     # retorna el número antes del '½' y lo sustituye por '.30'
    return time_to_beat 
def meta(name):
    scraper = Scraper()
    query = Query(name)
    url = query.get_url()
    if(url == "mal"):
        game = Resource(name, 5)
        
        return game
    else:
        game = scraper.get(url)
        game.metascore = round(game.metascore/20)
        print_resource_data(game)
        return game


# Contains info about the query to be made
class Query(object):
    # Standard constructor (w/ parameters)
    def __init__(self, terms):
        self.terms = terms
        self.base_url = "http://www.metacritic.com/search/game"
        self.url = self.base_url + "/" + terms + "/results"
    # Returns the URL of the created query

    def get_url(self):
        scra = Scraper()
        auxurl = scra.search(self.url)
        if(auxurl == "mal"):
            return auxurl
        else:
            urlf = "http://www.metacritic.com"+scra.search(self.url)
            return urlf

# This class represents a generic resource found at Metacritic


class Resource(object):
    def __init__(self, name, metascore):
        self.name = name
        self.metascore = metascore


class Response(object):
    def __init__(self, status, content):
        self.status = status
        self.content = content

    def valid(self):
        return (self.status == 200)


class Browser(object):
    def get(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        request = requests.get(url, headers=headers)

        response = Response(request.status_code, request.content)
        return response


class Scraper(object):
    def __init__(self):
        self.browser = Browser()
        self.response = ""
        self.soup = ""

    def get(self, url):
        self.response = self.browser.get(url)

        self.soup = bs4.BeautifulSoup(
            self.response.content, features="html.parser")

        return self.extract_data()

    def search(self, url):
        self.response = self.browser.get(url)

        self.soup = bs4.BeautifulSoup(
            self.response.content, features="html.parser")

        return self.extract_url()

    def extract_url(self):
        titles = self.soup.select(".product_title")
        if(titles == []):
            return("mal")
        else:
            try:
                for a in titles[0].find_all('a', href=True):
                    url = a['href']

                return url
            except:
                print("error")
                return ("mal")

    def extract_data(self):
        name = self._extract_name()
        metascore = self._extract_metascore()
        resource = Resource(name, metascore)
        return resource

    def _extract_name(self):
        titles = self.soup.select(".product_title")

        try:

            title = titles[0].text
            info = title.split("\n")
            name = info[2].strip()
            return name
        except:
            print(error)
            return ("mal")

    def _extract_metascore(self):
        section = self.soup.select(".metascore_wrap")[0]

        score = section.select(".metascore_w")[0].text

        return int(score)

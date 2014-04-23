#!/usr/bin/env python
import sys
import urllib2
import urlparse
import string
from bs4 import BeautifulSoup


class Crawler():

    links_to_consider = []
    links_on_page = []
    images = []
    js = []
    media = []

    def __init__(self, parent_link):
        """This class takes a URL and provides methods to
        obtain the static assets on its page"""

        hdr = {'User-Agent': "Magic Browser"}
        self.parent_link = parent_link
        try:
            req = urllib2.Request(self.parent_link, headers=hdr)
            src = urllib2.urlopen(req).read()
            self.bs = BeautifulSoup(src, "lxml")
            self.extractJS()
            self.extractMedia()
            self.extractLinks()
            self.extractImages()
        except:
            raise Exception(
                "The Crawler cannot initiate a connection to the provided link")

    def rDups(self, lst_of_things):
        """Given a list, removes duplicates"""
        return list(set(lst_of_things))

    def getAssets(self):
        """Returns a dict of asset types and URLs"""
        return {
            "Links": self.rDups(self.links_on_page), "Images": self.rDups(self.images),
            "JS": self.rDups(self.js), "Media": self.rDups(self.media),
            "Consider_Links": self.rDups(self.links_to_consider),
            "Links": self.rDups(self.links_on_page)
        }

    def getAbsURL(self, incomplete_url):
        """Returns an absolute URL given a relative one"""

        absUrl = urlparse.urljoin(self.parent_link, incomplete_url)
        parsedUrl = urlparse.urlparse(absUrl)
        if parsedUrl.port == 80:
            hostUrl = parsedUrl.netloc[:-3]
        else:
            hostUrl = parsedUrl.netloc
        absUrl = urlparse.urlunparse(
            (parsedUrl.scheme, hostUrl, parsedUrl.path,
                parsedUrl.params, parsedUrl.query, parsedUrl.fragment))
        return absUrl.strip()

    def extractJS(self):
        """Computes a list of JS files needed by the
        application
        """
        for i in self.bs.findAll('script', {"src": True}):

            absUrl = self.getAbsURL(i['src'])
            self.js.append(absUrl)

    def extractMedia(self):
        """Computes a list of Media files"""

        for i in self.bs.findAll('link', {'href': True}):
            absUrl = self.getAbsURL(i['href'])
            self.media.append(absUrl)

    def extractImages(self):
        """Computes a list of image URLS"""
        for i in self.bs.findAll('img', {'src': True}):
            absUrl = self.getAbsURL(i['src'])
            self.images.append(absUrl)

    def extractLinks(self):
        """Computes a list of absolute links on the page"""

        tags = self.bs.findAll('a', {'href': True})
        for link in tags:
            absUrl = self.getAbsURL(link['href'])
            self.links_on_page.append(absUrl)
            parsedUrl = urlparse.urlparse(absUrl)
            if parsedUrl.netloc == urlparse.urlparse(self.parent_link).netloc:
                self.links_to_consider.append(absUrl)

if __name__ == "__main__":

    consider_links = []
    seen_links = []
    consider_links.append("https://www.digitalocean.com/")
    while len(consider_links) > 0:
        l = consider_links.pop()
        seen_links.append(l)
        print l
        try:
            c = Crawler(l)
            # print c.getAssets()
            new_links = c.getAssets()["Consider_Links"]
            for link in new_links:
                if link not in seen_links:
                    consider_links.append(link)
        except:
            continue

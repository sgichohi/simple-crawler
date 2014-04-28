#!/usr/bin/env python
import sys
import urllib2
import urlparse
import string
import json
from bs4 import BeautifulSoup


class PageExtractor():

    links_to_consider = []
    links_on_page = []
    images = []
    js = []
    media = []

    def __init__(self, parent_link, src):
        """This class takes a URL and provides methods to
        obtain the static assets on its page"""

        self.parent_link = parent_link
        self.src = src
        self.bs = BeautifulSoup(self.src, "lxml")
        self.extractJS()
        self.extractMedia()
        self.extractLinks()
        self.extractImages()

    def rDups(self, lst_of_things):
        """Given a list, removes duplicates"""
        return list(set(lst_of_things))

    def getAssets(self):
        """Returns a dict of asset types and URLs"""
        static = self.rDups(self.js + self.images + self.media)
        # print static
        # print list(set(self.links_to_consider) - set(static))
        return {
            "Links": self.rDups(self.links_on_page),
            "Static": static,
            "Consider_Links": list(set(self.links_to_consider) - set(static)),
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


def makeConn(parent_link):
    hdr = {'User-Agent': "Magic Browser"}
    try:
        req = urllib2.Request(parent_link, headers=hdr)
        src = urllib2.urlopen(req).read()

    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        raise Exception(
            "The Crawler cannot initiate a connection to the provided link")
    return src


def crawl(url):

    consider_links = set()
    seen_links = set()
    sitemap = {}
    consider_links.add(url)
    while len(consider_links) > 0:
        l = consider_links.pop()
        seen_links.add(l)

        try:
            src = makeConn(l)
            c = PageExtractor(l, src)
            assets = c.getAssets()
            new_links = assets["Consider_Links"]
            seen_links.update(assets["Static"])
            sitemap[l] = {"Static Assets": assets[
                          "Static"], "Links": assets["Links"]}

            for link in new_links:

                if link not in seen_links:
                    consider_links.add(link)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            continue
    return sitemap
if __name__ == "__main__":
    try:
        root = sys.argv[1]

    except IndexError:
        print "  Usage: ./crawl.py link"
        print "  Example: ./crawl.py http://cool.com/"
        exit()
    try:
        print json.dumps(crawl(root), sort_keys=True, indent=4)
    except:
            raise

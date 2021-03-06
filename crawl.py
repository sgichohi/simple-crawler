#!/usr/bin/env python
from __future__ import print_function
import gevent.monkey

gevent.monkey.patch_all()
import gevent.pool

import sys
import requests
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
        self.js = self.extractJS()
        self.media = self.extractMedia()
        self.links_on_page, self.links_to_consider = self.extractLinks()
        self.images = self.extractImages()

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
        return (absUrl.partition("#")[0]).strip()

    def extractJS(self):
        """Computes a list of JS files needed by the
        application
        """
        js = []
        for i in self.bs.findAll('script', {"src": True}):

            absUrl = self.getAbsURL(i['src'])
            js.append(absUrl)
        return js

    def extractMedia(self):
        """Computes a list of Media files"""
        media = []
        for i in self.bs.findAll('link', {'href': True}):
            absUrl = self.getAbsURL(i['href'])
            media.append(absUrl)
        return media

    def extractImages(self):
        """Computes a list of image URLS"""
        images = []
        for i in self.bs.findAll('img', {'src': True}):
            absUrl = self.getAbsURL(i['src'])
            images.append(absUrl)
        return images

    def extractLinks(self):
        """Computes a list of absolute links on the page"""

        links_to_consider = []
        links_on_page = []
        tags = self.bs.findAll('a', {'href': True})
        for link in tags:
            absUrl = self.getAbsURL(link['href'])
            links_on_page.append(absUrl)
            parsedUrl = urlparse.urlparse(absUrl)
            if parsedUrl.netloc == urlparse.urlparse(self.parent_link).netloc:
                links_to_consider.append(absUrl)
        return links_on_page, links_to_consider


def makeConn(parent_link):
    """Makes a connection to a web page"""
    hdr = {'User-Agent': "Magic Browser"}
    try:

        # req = urllib3.Request(parent_link, headers=hdr)

        # print(parent_link)
        src = requests.get(parent_link, verify=False, headers=hdr)
        c = PageExtractor(parent_link, src.content)

    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        return None

    return c


def crawl(url, pool_count=1000):
    """Takes a url and prints to stdout a list of static assets and links
    on each linked page in the domain as a JSON object

    {
    "Link: {
        "Links": [],
        "Static Assets": [

        ]
    }
}

    """
    consider_links = []
    seen_links = set()
    sitemap = {}
    pool = gevent.pool.Pool(pool_count)
    consider_links.append(url)

    while len(consider_links) > 0:

        results = pool.map(makeConn, consider_links)
        seen_links.update(consider_links)
        del consider_links[:]
        for c in results:
            if c is None:
                continue

            assets = c.getAssets()
            seen_links.update(assets["Static"])
            sitemap[c.parent_link] = {"Static Assets": assets[
                                      "Static"], "Links": assets["Links"]}

            for link in assets["Consider_Links"]:

                if link not in seen_links:
                    consider_links.append(link)

    return sitemap
if __name__ == "__main__":
    try:
        root = sys.argv[1]

    except IndexError:
        print("  Usage: ./crawl.py link", file=sys.stderr)
        print("  Example: ./crawl.py http://cool.com/", file=sys.stderr)
        exit()
    try:

        print(json.dumps(crawl(root), sort_keys=True, indent=4))
    except:
        raise

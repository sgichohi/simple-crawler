#!/usr/bin/env python
import unittest
import crawl


class CrawlerTest(unittest.TestCase):

    def setUp(self):

        with open("index.html", 'r') as test_file:
            self.src = test_file.read()
            self.parent_url = "http://labta.cs.princeton.edu/"
            self.page_ex = crawl.PageExtractor(self.parent_url, self.src)

    def testextractJS(self):

        res = self.page_ex.extractJS()
        true = [
            "https://ajax.googleapis.com/ajax/libs/jquery/2.0.3/jquery.min.js",
            "https://netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js"]
        self.assertEqual(
            sorted(res), sorted(true))

    def testextractMedia(self):
        res = self.page_ex.extractMedia()

        true = [
            "https://netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css",
        ]
        self.assertEqual(
            sorted(res), sorted(true))

    def testextractLinks(self):

        res, res1 = self.page_ex.extractLinks()

        true1 = ['http://labta.cs.princeton.edu/s14-sched-reading.html',
                 'http://labta.cs.princeton.edu/s14-sched_126226217.html',
                 'http://labta.cs.princeton.edu/info.html', 'http://labta.cs.princeton.edu/studentguide.html',
                 'http://labta.cs.princeton.edu/f13-sched_109126226217.html',
                 'http://labta.cs.princeton.edu/s13-sched_126226217.html',
                 'http://labta.cs.princeton.edu/f12-sched_126226217.html',
                 'http://labta.cs.princeton.edu/s12-sched_126226217.html', 'http://labta.cs.princeton.edu/f11-sched_126226217.html',
                 'http://labta.cs.princeton.edu/sched_126226217.html', 'http://labta.cs.princeton.edu/f10-sched_126226217.html',
                 'http://labta.cs.princeton.edu/f10-sched_109.html']

        true = [
            'http://labta.cs.princeton.edu/s14-sched-reading.html',
            'https://docs.google.com/spreadsheet/ccc?key=0AtnQ9z7kCBHVdFFEbnhsTlE4dm1ZUGg4RnZCdlVfX2c&usp=sharing',
            'http://labta.cs.princeton.edu/s14-sched_126226217.html', 'http://labta.cs.princeton.edu/info.html',
            'http://labta.cs.princeton.edu/studentguide.html', 'http://labta.cs.princeton.edu/f13-sched_109126226217.html',
            'http://labta.cs.princeton.edu/s13-sched_126226217.html', 'http://labta.cs.princeton.edu/f12-sched_126226217.html',
            'http://labta.cs.princeton.edu/s12-sched_126226217.html', 'http://labta.cs.princeton.edu/f11-sched_126226217.html',
            'http://labta.cs.princeton.edu/sched_126226217.html',
            'http://labta.cs.princeton.edu/f10-sched_126226217.html', 'http://labta.cs.princeton.edu/f10-sched_109.html']

        self.assertEqual(
            sorted(res), sorted(true))
        self.assertEqual(
            sorted(res1), sorted(true1))

    def testextractImages(self):

        res = self.page_ex.extractImages()
        true = [
            'http://www.chow.com/uploads/6/6/2/385266_smiley_face_tiny.jpeg']

        self.assertEqual(
            sorted(res), sorted(true))


def main():
    unittest.main()

if __name__ == '__main__':
    main()

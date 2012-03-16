__author__ = 'Deane Barker'

import urllib2
import re

class BaseSignature(object):
    
    NAME = 'Base Signature Class.  OVERRIDE'
    WEBSITE = 'http://www.acme.org OVERRIDE'
    KNOWN_POSITIVE = 'http://www.acme.org OVERRIDE'

    cached_pages = {}
    
    def run(self, url):
        """
        Runs through all of the test methods (identified by beginning
        with the string "test") and returns a confidence score.
        """
        
        confidence_score = 0
        
        tests = []
        for m in dir(self):
            if m.startswith('test'):
                tests.append(getattr(self, m))
        
        if not len(tests):
            raise SystemError("There are no tests!")
                
        for test in tests:
            conf = test(url)        
            if conf == 100:
                # This test is absolutely certain
                return 1
            elif conf > 0:
                # Test found a clue
                confidence_score += 1
            elif conf < 0:
                # Test ruled out this CMS
                confidence_score = 0
                break
        
        return confidence_score/len(tests)

    def get_page(self, url):
        """
        Returns a page from local cache if we have it, otherwise requests it and puts it in local cache.
        """

        # If it's in local cache, just return it
        if self.cached_pages.has_key(url):
            return self.cached_pages[url]

        # Get it
        try:
            page = urllib2.urlopen(url, timeout=2)
        except urllib2.HTTPError, IOError:
            return False

        # Technically, any status code starting with "2" is valid...
        if str(page.getcode())[0] != '2':
            return False

        # Put it in the cache
        self.cached_pages[url] = page

        # QUESTION: do we have to call page.close?  I didn't find much doc on this.

        return page

    def get_url_stem(self, url):
        """
        Returns the stem of the URL.  
        
        For example, if the URL is http://www.acme.com/foo/bar, 
        
        The stem would be http://www.acme.com
        
        """
        
        return '/'.join(url.split('/')[:3])
        
    def page_contains_pattern(self, url, pattern):
        """
        Returns True if the given page contains a particular string.
        """
        result = False
        rgx = re.compile(pattern)
        
        page = self.get_page(url)

        # Just in case it threw an error
        if not page:
            return False

        for line in page:
            if rgx.search(line):
                result = True
                break

        return result
        
    def url_exists(self, url):
        """
        Returns True if the URL exists
        
        """
        return self.get_page(url)

    def is_dot_net_webforms(self, url):
        """
        Returns True is the URL has .Net markers.
        """
        result = False

        page = self.get_page(url)

        if 'x-powered-by' in page.headers:
            if page.headers['x-powered-by'] == 'ASP.NET':
                result = True

        pattern = 'id="aspnetform"'
        if page_contains_pattern(url, pattern):
            result = True

        pattern = 'ct100_'
        if page_contains_pattern(url, pattern):
            result = True

        pattern = 'name="__VIEWSTATE"'
        if page_contains_pattern(url, pattern):
            result = True

        return result
    
class SampleSignature(BaseSignature):
    """
    SampleSignature is a very basic example of how to extend BaseSignature
    
    """
    
    def test_anything(self, url):
        """
        Just verifies that the url string is not null
        
        """
        if url:
            return True
        else:
            return False
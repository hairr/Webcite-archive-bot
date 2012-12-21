"""
This code was written by Hair <hairrazerrr@gmail.com>
It was heavily based off of Lowercase Sigmabot III off of wikipedia <https://github.com/legoktm/webcite-bot/>
Thanks for everything.
"""

import re
import urllib
import urllib2
import cookielib
import mwhair
import mwparserfromhell as mw
import time
import datetime
import sqlite3 as lite
from bs4 import BeautifulSoup as BS


class WebCiteArchiveBot(object):
    def __init__(self, username, password):
        """
        Initializing!~
        """
        mwhair.site('http://runescape.wikia.com/api.php')
        mwhair.login(username, password)
        self.site = "http://webcitation.org/archive"
        self.params = {'email':'hairrazerrr@gmail.com', 'returnxml':'true'}
        self.cite_templates = ['citedevblog', 'citedevdiary', 'citeforum',
        'citegodletter', 'citelore', 'citenews', 'citenpc',
        'citepoll', 'citepostbag', 'citesupport', 'citegeneral',
        'citepub', 'plaincitedevblog', 'plaincitedevdiary', 'plainciteforum',
        'plaincitegodletter', 'plaincitelore', 'plaincitenews', 'plaincitenpc',
        'plaincitepoll', 'plaincitepostbag']
        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.opener.add_headers = {('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5)' \
                                   'AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64')}
        self.cite_template = '{{CiteGeneral|url=%s|title=%s|' \
                             'accessdate=%s|archiveurl=%s|archivedate=%s}}'
        self.plain_cite_template = '{{PlainCiteGeneral|url=%s|title=%s|' \
                                   'accessdate=%s|archiveurl=%s|archivedate=%s}}'

    def format_date(self):
        """
        Used for dates withen cite templates
        """
        now = datetime.datetime.utcnow()
        return now.strftime('%d %B %Y')

    def get_pages(self):
        """
        Get's all of our lovely pages
        """
        return mwhair.allpages(limit='max', namespace=0)

    def get_title(self, url):
        """
        Get's the page title to the url specified
        """
        try:
            content = opener.open(url)
        except:
            return None
        try:
            soup = BS(content.read())
        except TypeError:
            print 'Error occured with %s' % url
            return None
        title = soup.title.string.strip()
        title = title.replace('|', '{{!}}')
        title = title.replace('\n', '')
        title = re.sub(r'\s+', ' ', title)
        return title

    def get_links(self, text):
        """
        Gets all the urls on the page
        """
        regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(regex, text)
        return urls

    def archive(self, url):
        """
        Archive the url at webcitation.org; returns None if unsuccessful
        """
        conn = lite.connect('links.db')
        curr = conn.cursor()
        curr.execute("SELECT archived FROM links WHERE url ='%s'" % url)
        archived_url = curr.fetchall()[0][0]
        if archived_url:
            conn.close()
            return archived_url
        new_params = self.params
        new_params['url'] = url
        data = urllib.urlencode(new_params)
        content = self.opener.open(self.site, data)
        soup = BS(content.read())
        try:
            archived_url = str(soup.archiverequest.resultset.webcite_url.string)
            curr.execute('INSERT INTO links (?,?)',(url, archived_url, ))
            conn.close()
            return archived_url
        except:
            conn.close()
            return None

    def get_forum_code(self, url):
        regex = re.compile(r'http://services\.runescape\.com/m=forum/forums\.ws\?(.{,3},.{,3}),(.*)')
        match = regex.findall(url)[0][0]
        return match

    def add_in_template(self, text, url, archiveurl):
        """
        Magic happens here, adds in the url to the template
        """
        forum_codes = {
        '311,312':'Combat News Hub',
        '296,297':'Combat Discussion',
        '294,295':'News Discussion',
        '309,310':"Solomon's General Store",
        '312,313':'Squeal of Fortune',
        '15,16':'Recent Game Updates',
        '16,17':'Future Game Updates',
        '74,75':'Existing Game Content',
        '185,186':'New Game Content - Suggestions',
        '278,279':'Website and Forums',
        '277,278':'Other - Discussion & Suggestions',
        '14,15':'General',
        '48,49':'Goals and Achievements',
        '75,76':'Distractions and Diversions',
        '46,47':'Roleplaying - Forums',
        '237,238':'Roleplaying - In-Game',
        '254,255':'Community Home',
        '298,299':'RuneScape Videos!',
        '198,199':'Developer Blogs',
        '103,104':'Contact Customer Support',
        '250,251':'Account Help',
        '25,26':'Tech Support',
        '291,292':'Billing Support',
        '275,276':'Safety Centre',
        '42,43':'Events - Regular and Ongoing',
        '199,200':'Events - "One Off"',
        '201,202':'Businesses & Services',
        '235,236':'RuneFest',
        '268,269':'Clan Help',
        '94,95':'Recruitment - Looking for a clan',
        '87,88':'Recruitment - Under 140 Combat',
        '269,270':'Recruitment - 140-175 Combat',
        '92,93':'Recruitment - 175 Combat and over',
        '288,289':'Recruitment - Skilling Clans',
        '289,290':'Recruitment - Questing & Minigame Clans',
        '290,291':'Recruitment - Social & Community Clans',
        '93,94':'Recruitment - Specialist Clans',
        '90,91':'Clan Home',
        '135,136':'Clan Discussion',
        '271,272':'Clans Feedback',
        '17,18':'Item Discussion',
        '20,21':'Quests',
        '21,22':'Clue Scrolls',
        '19,20':'Monsters',
        '154,155':'Skills',
        '98,99':'Guides',
        '71,72':'Achievement & Challenge System',
        '194,195':'Teamwork',
        '45,46':'PvP',
        '148,149':'Adventuring Parties',
        '150,151':'Dungeoneering Help',
        '23,24':'Off Topic',
        '49,50':'Stories',
        '55,56':'Forum Games',
        '181,182':'Compliments',
        '39,40':'Armour',
        '38,39':'Weapons',
        '31,32':'Fletching',
        '40,41':'Treasure Trail Items',
        '37,38':'Crafting',
        '33,34':'Food',
        '36,37':'Discontinued Items',
        '35,36':'Ores and Bars',
        '32,33':'Farming',
        '56,57':'Construction',
        '59,60':'Summoning',
        '41,42':'Miscellaneous',
        '51,52':'RSC Community',
        '50,51':'RSC Discussion',
        '54,55':'RSC Feedback'
        }
        original = text
        code = mw.parse(text)
        for template in code.filter_templates():
            lowercase = template.name.lower()
            if lowercase in self.cite_templates:
                if not template.has_param('url'):
                    continue  # What are we doing here
                if template.has_param('archiveurl'):
                    continue  # Already taken care of :)
                if template.get('url').value.strip() != url:
                    continue
                if not template.has_param('accessdate'):
                    template.add('accessdate', self.format_date())
                else:
                    template.get('accessdate').value.replace(template.get('accessdate').value,
                    self.format_date())
                if lowercase == 'citeforum' and not lowercase.has_param('title'):
                    forum_code = self.get_forum_code(url)
                    template.add('title',forum_codes[forum_code])
                if 'webcitation.org' in template.get('url').value.strip():
                    continue
                template.add('archiveurl', archivurl)
                template.add('archivedate', self.format_date())
                break
        if str(original) != str(code):
            return str(code)
        regex = re.match(r'<ref(.*?)>\w?\[\w?%s\w?(.*?)\]\w?</ref>' % re.escape(url),
        str(code), flags=re.IGNORECASE)
        if regex:
            if regex.match(2) == '':
                title = self.get_title(url)
            else:
                title = regex.match(2)
            template = self.cite_template % (url, title, self.format_date(),
            archiveurl, self.format_date())
            cite_template = '<ref%s>%s</ref>' % (regex.match(1), template)
            new_text = str(code).replace(regex.group(0), cite_template)
            return new_text  
        regex = re.match(r'\[\w?%s\w?(.*?)\]' % re.escape(url), 
        str(code), flags=re.IGNORECASE)
        if regex:
            if regex.match(1) == '':
                title = self.get_title(url)
            else:
                title = regex.match(1)
                new_template = self.plain_cite_template % (url, title,
                self.format_date(), archive_url, self.format_date())
                new_text = str(code).replace(regex.group(0), new_template)
                return new_text
        return str(code)

    def run(self):
        """
        aaannndddd begin
        """
        pages = self.get_pages()
        for page in pages:
            print "Viewing page: " + page
            urls, new_text = [], None
            try:
                text = mwhair.edit(page)
            except UnicodeEncodeError:
                print "UnicodeEncodeError: " + page
            except:
                print "Unknown Error for " + page
            time.sleep(1)
            links = self.get_links(text)
            if links:
                for link in links:
                    print "Found url: " + link
                    archived_link = self.archive(link)
                    if archived_link is None:
                        continue
                    urls.append((link,
                                archived_link))
                    time.sleep(31)  # At 30 seconds we'll be rejected
                for url in urls:
                    if new_text:
                        new_text = self.add_in_template(new_text,
                        url[0], url[1])
                    else:
                        new_text = self.add_in_template(text,
                        url[0], url[1])
                    if text != new_text:
                        print "Saving page: " + page
                        mwhair.save(page, text=new_text,
                        summary="Archiving urls in cite templates", minor=True)

if __name__ == '__main__':
    username, password = raw_input("Username: "), raw_input("Password: ")
    bot = WebCiteArchiveBot(username, password)
    bot.run()

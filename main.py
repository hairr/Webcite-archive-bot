"""
This code was written by Hair <hairrazerrr@gmail.com>
It was heavily based off of Lowercase Sigmabot III off of wikipedia <https://github.com/legoktm/webcite-bot/>
Thanks for everything.
"""

import urllib
import urllib2
import cookielib
import mwhair
import mwparserfromhell as mw
import time
import datetime
import sqlite3 as lite
from bs4 import BeautifulSoup as BS

class WebCiteArchiveBot:
	def __init__(self,username,password):
		"""
		Initializing!~
		"""
		mwhair.site('http://runescape.wikia.com/api.php')
		mwhair.login(username,password)
		self.site = "http://webcitation.org/archive"
		self.params = {'email':'hairrazerrr@gmail.com','returnxml':'true'}
		self.cite_templates = ['citedevblog','citedevdiary','citeforum','citegodletter','citelore','citenews','citenpc',
								'citepoll','citepostbag','citesupport','citegeneral','citepub','plaincitedevblog','plaincitedevdiary',
								'plainciteforum','plaincitegodletter','plaincitelore','plaincitenews','plaincitenpc','plaincitepoll',
								'plaincitepostbag']
		self.cj = cookielib.CookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		self.opener.add_headers = {('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64')}
		self.cite_template = '{{CiteGeneral|url=%s|title=%s|accessdate=%s|archiveurl=%s|archivedate=%s}}'
		site.plain_cite_template = '{{PlainCiteGeneral|url=%s|title=%s|accessdate=%s|archiveurl=%s|archivedate=%s}}'

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
		return mwhair.allpages(limit='max',namespace=0)

	def get_title(self,url):
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
		title = title.replace('|','{{!}}')
		title = title.replace('\n','')
		title = re.sub(r'\s+',' ',title)
		return title

	def get_links(self, text):
		"""
		Gets all the urls on the page
		"""
		urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
		return urls

	def archive(self,url):
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
		content = self.opener.open(self.site,data)
		soup = BS(content.read())
		try:
			archived_url = str(soup.archiverequest.resultset.webcite_url.string)
			curr.execute('INSERT INTO links (?,?)',(url,archived_url))
			conn.close()
			return archived_url
		except:
			conn.close()
			return None

	def add_in_template(self, text, url, archiveurl):
		"""
		Magic happens here, adds in the url to the template
		"""
		original = text
		code = mw.parse(text)
		for template in code.filter_templates():
			lowercase = template.name.lower()
			if lowercase in self.cite_templates:
				if not template.has_param('url'):
					continue # What are we doing here
				if template.has_param('archiveurl'):
					continue # Already taken care of :)
				if template.get('url').value.strip() != url:
					continue
				if not template.has_param('accessdate'):
					template.add('accessdate',self.format_date())
				else:
					template.get('accessdate').value.replace(template.get('accessdate').value,self.format_date())
				template.add('archiveurl',archivurl)
				template.add('archivedate',format_date())
				break
		if str(original) != str(code):
			return str(code)
		# not in a template :/
		regex = re.match(r'<ref(.*?)>\w?\[\w?%s\w?(.*?)\]\w?</ref>' % re.escape(url), str(code), flags=re.IGNORECASE)
		if regex:
			if regex.match(2) == '':
				title = self.get_title(url)
			else:
				title = regex.match(2)
			template = self.cite_template % (url, title, self.format_date(), archiveurl, self.format_date())
			cite_template = '<ref%s>%s</ref>' % (regex.match(1), template)
			new_text = str(code).replace(regex.group(0), cite_template)
			return new_text
		# Doesn't have a ref.. must be a plain url then?
		regex = re.match(r'\[\w?%s\w?(.*?)\]' % re.escape(url), str(code), flags=re.IGNORECASE)
		if regex:
			if regex.match(1) == '':
				title = self.get_title(url)
			else:
				title = regex.match(1)
			new_template = self.plain_cite_template % (url, title, self.format_date(), archive_url, self.format_date())
			new_text = str(code).replace(regex.group(0), new_template)
			return new_text
		return str(code) # the link is a lost cause

	def run(self):
		"""
		aaannndddd begin
		"""
		pages = self.get_pages()
		for page in pages:
			urls, new_text = [], None
			text = mwhair.edit(page)
			time.sleep(1)
			links = self.get_links(text)
			if links:
				for link in links:
					archived_link = self.archive(link)
					if archived_link == None:
						continue
					urls.append((link,archived_link))
					time.sleep(31) # At 30 seconds we'll be rejected, better safe than sorry :P
				for url in urls:
					if new_text:
						new_text = self.add_in_template(new_text,url[0],url[1])
					else:
						new_text = self.add_in_template(text,url[0],url[1])
				mwhair.save(page,text=new_text,summary="Archiving urls in cite templates",minor=True)

if __name__ == '__main__':
	username, password = raw_input("Username: "),raw_input("Password: ")
	bot = WebCiteArchiveBot(username,password)
	bot.run()
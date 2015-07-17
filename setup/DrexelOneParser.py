#!/usr/bin/python

from SiteParser import SiteParser

class DrexelOneParser(SiteParser):
	def __init__(self, database, username, password):
		SiteParser.__init__(self, database)

	def parse(self):
		SiteParser.parse(self)
		self.cleanup()

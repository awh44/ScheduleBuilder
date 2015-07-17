#!/usr/bin/python

import sys

from SiteParser import SiteParser
from TMSParser import TMSParser
from DrexelOneParser import DrexelOneParser

def main(argv):
	if len(argv) < 2:
		print "Supply which site should be parsed, either 'one' or 'tms', as a command line argument."
		return 1

	if argv[1] == "one":
		if len(argv) < 4:
			print "Please supply a username and password as command line arguments."
			return 1
		parser = DrexelOneParser("courses_500.db", sys.argv[2], sys.argv[3])
	elif argv[1] == "tms":
		parser = TMSParser("courses_500.db")

	else:
		print "Parser type not recognized. Please use either 'one' or 'tms' as the first command line argument."
		return 1

	parser.parse()


if __name__ == "__main__":
	sys.exit(main(sys.argv))

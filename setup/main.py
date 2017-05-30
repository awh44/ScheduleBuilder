#!/usr/bin/python

import sys
import traceback

from SiteParser import SiteParser
from TMSParser import TMSParser
from DrexelOneParser import DrexelOneParser

def is_one_parser(parser_type):
	return parser_type == "one"

def is_tms_parser(parser_type):
	return parser_type == "tms"

def create_one_parser(username, password):
	return DrexelOneParser("courses_500.db", username, password)

def create_tms_parser():
	return TMSParser("courses_500.db")

def main(argv):
	if len(argv) < 2:
		print "Supply which site should be parsed, either 'one' or 'tms', as a command line argument."
		return 1

	if is_one_parser(argv[1]):
		if len(argv) < 4:
			print "Please supply a username and password as command line arguments."
			return 1
		parser = create_one_parser(argv[2], argv[3])
	elif is_tms_parser(argv[1]):
		parser = create_tms_parser()

	else:
		print "Parser type not recognized. Please use either 'one' or 'tms' as the first command line argument."
		return 1
	
	for tries in range(10):
		try:	
			parser.parse()
		except Exception, err:
			traceback.print_exc()
			parser.cleanup()
			parser = create_one_parser(argv[2], argv[3]) if is_one_parser(argv[1]) else create_tms_parser()

if __name__ == "__main__":
	sys.exit(main(sys.argv))

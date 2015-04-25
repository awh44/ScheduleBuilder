#!/usr/bin/python

import sqlite3
import sys

print "hi", sys.argv[1]
conn = sqlite3.connect("../data/courses.db")
print "ho"
c = conn.cursor()
print "hum"
results = c.execute("SELECT * FROM courses WHERE subj_id = ?", (sys.argv[1],))
print "fiddle"
print results.fetchone()
print "dee"

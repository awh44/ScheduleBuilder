#!/usr/bin/python

import sqlite3

conn = sqlite3.connect("../data/courses.db")
c = conn.cursor()
results = c.execute("SELECT subj_id, name FROM subjects ORDER BY name")
result = results.fetchone()
while result != None:
	print "<option value=\"" + result[0] + "\">" + result[1] + "</option>"
	result = results.fetchone()

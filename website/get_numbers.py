#!/usr/bin/python

import sqlite3
import sys

conn = sqlite3.connect("../data/courses.db")
c = conn.cursor()
results = c.execute("SELECT * FROM courses WHERE subj_id = ?", (sys.argv[1],))
print results.fetchone()

#!/usr/bin/python

import json
import sqlite3
import sys

import dict_factory

conn = sqlite3.connect("../data/courses.db")
conn.row_factory = dict_factory.dict_factory
c = conn.cursor()
print json.dumps(c.execute("SELECT course_id, number, name FROM courses WHERE subj_id = ? ORDER BY number", (sys.argv[1],)).fetchall())

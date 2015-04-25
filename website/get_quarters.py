#!/usr/bin/python

import json
import sqlite3
import sys

import dict_factory

conn = sqlite3.connect("../data/courses.db")
conn.row_factory = dict_factory.dict_factory
c = conn.cursor()
results = c.execute('''SELECT q.quarter FROM quarters q
                        	LEFT JOIN quarters_for_courses qc ON qc.quarter_id = q.quarter_id
                        	LEFT JOIN courses c ON c.course_id = qc.course_id
                       WHERE c.course_id = ?''', (sys.argv[1],))
json_results = []
result = results.fetchone()
while result != None:
	json_results.append(result["quarter"])
	result = results.fetchone()

print json.dumps(json_results)

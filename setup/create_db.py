#!/usr/bin/python

import sqlite3

conn = sqlite3.connect("../data/courses.db")
c = conn.cursor()

c.execute("CREATE TABLE departments(dept_id TEXT PRIMARY KEY, name TEXT)")
c.execute("CREATE TABLE courses(course_id INTEGER PRIMARY KEY, dept_id TEXT, number INTEGER, FOREIGN KEY(dept_id) REFERENCES departments(dept_id))")
c.execute("CREATE TABLE quarters(quarter_id INTEGER PRIMARY KEY, quarter TEXT)")
c.execute("CREATE TABLE quarters_for_courses(quarter_id INTEGER, course_id INTEGER, FOREIGN KEY(quarter_id) REFERENCES quarters(quarter_id), FOREIGN KEY(course_id) REFERENCES courses(course_id))")

conn.commit()
conn.close()

#!/usr/bin/python

import sqlite3

conn = sqlite3.connect("../data/courses.db")
c = conn.cursor()

c.execute("CREATE TABLE subjects(subj_id TEXT PRIMARY KEY, name TEXT)")
c.execute('''CREATE TABLE courses(course_id INTEGER PRIMARY KEY,
                                  subj_id TEXT,
                                  number INTEGER,
                                  name TEXT,
                                  FOREIGN KEY(subj_id) REFERENCES subjects(subj_id))''')
c.execute('''CREATE TABLE quarters(quarter_id INTEGER PRIMARY KEY,
                                   season TEXT,
                                   year TEXT)''')
c.execute('''CREATE TABLE course_quarter_map(course_quarter_id INTEGER PRIMARY KEY,
                                             course_id INTEGER,
                                             quarter_id INTEGER,
                                             FOREIGN KEY(course_id) REFERENCES courses(course_id),
                                             FOREIGN KEY(quarter_id) REFERENCES quarters(quarter_id))''')
c.execute('''CREATE TABLE course_instances(instance_id INTEGER PRIMARY KEY,
                                           course_quarter_id INTEGER,
                                           CRN INTEGER,
                                           campus TEXT,
                                           days TEXT,
                                           start TEXT,
                                           end TEXT,
                                           capacity INTEGER,
                                           taken INTEGER,
                                           instructor_id INTEGER,
                                           FOREIGN KEY(course_quarter_id) REFERENCES course_quarter_map(course_quarter_id),
                                           FOREIGN KEY(instructor_id) REFERENCES instructors(instructor_id))''')
c.execute('''CREATE TABLE instructors(instructor_id INTEGER PRIMARY KEY,
                                      name TEXT)''')
conn.commit()
conn.close()

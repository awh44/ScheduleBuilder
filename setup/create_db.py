#!/usr/bin/python

import sqlite3

conn = sqlite3.connect("../data/new_courses.db")
c = conn.cursor()

c.execute("CREATE TABLE subjects(subj_id TEXT PRIMARY KEY, name TEXT)")
c.execute('''CREATE TABLE courses(course_id INTEGER PRIMARY KEY,
                                  subj_id TEXT,
                                  number INTEGER,
                                  name TEXT,
                                  credits REAL,
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
                                           section TEXT,
                                           campus TEXT,
                                           capacity INTEGER,
                                           taken INTEGER,
                                           instructor_id INTEGER,
                                           FOREIGN KEY(course_quarter_id) REFERENCES course_quarter_map(course_quarter_id),
                                           FOREIGN KEY(instructor_id) REFERENCES instructors(instructor_id))''')
c.execute('''CREATE TABLE instructors(instructor_id INTEGER PRIMARY KEY,
                                      name TEXT)''')

c.execute("CREATE TABLE days(day_id INTEGER PRIMARY KEY, day TEXT)")
c.execute("INSERT INTO days(day_id, day) VALUES(0, 'Sunday')")
c.execute("INSERT INTO days(day_id, day) VALUES(1, 'Monday')")
c.execute("INSERT INTO days(day_id, day) VALUES(2, 'Tuesday')")
c.execute("INSERT INTO days(day_id, day) VALUES(3, 'Wednesday')")
c.execute("INSERT INTO days(day_id, day) VALUES(4, 'Thursday')")
c.execute("INSERT INTO days(day_id, day) VALUES(5, 'Friday')")
c.execute("INSERT INTO days(day_id, day) VALUES(6, 'Saturday')")

c.execute('''CREATE TABLE instance_time_map(instance_time_id INTEGER PRIMARY KEY,
                                            instance_id INTEGER,
                                            day_id INTEGER,
                                            start INTEGER,
                                            end INTEGER,
                                            FOREIGN KEY(instance_id) REFERENCES course_instances(instance_id),
                                            FOREIGN KEY(day_id) REFERENCES days(day_id))''')

conn.commit()
conn.close()

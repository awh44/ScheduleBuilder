#!/usr/bin/python

#import psycopg2
import sys
import sqlite3
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class SiteParser:
	campus_map = {
	                 u"UC": u"University City",
	                 u"BUR": "Burlington County College",
	                 u"SAC": u"Sacramento",
	                 u"CC": u"Center City",
	                 u"ONL": u"Online",
	                 u"PTS": "PTS",
	              }

	def __init__(self, database):
		self.conn = sqlite3.connect(database)
		self.c = self.conn.cursor()
		self.setup_checked_quarters()
		self.driver = webdriver.Firefox()
		campusobjs = self.c.execute("SELECT name FROM Campuses")
		for campusobj in campusobjs:
			self.campus_map[campusobj[0]] = campusobj[0]

	def cleanup(self):
		self.driver.close()
		self.conn.close()

	def ensure_quarter(self, quarter_id):
		quarterobj = self.c.execute("SELECT * FROM Terms WHERE season = ? AND term_type = ? AND year = ?", quarter_id).fetchone()
		if quarterobj == None:
			self.c.execute("INSERT INTO Terms(season, term_type, year) VALUES(?, ?, ?)", quarter_id)

	def ensure_subject(self, subject):
		subobj = self.c.execute("SELECT * FROM Subjects WHERE name = ?", (subject,)).fetchone()
		if subobj == None:
			self.c.execute("INSERT INTO Subjects(name) VALUES(?)", (subject,))

	def ensure_course(self, abbr, number, name, description, credits, subject):
		courseobj = self.c.execute("SELECT * FROM Courses_Have WHERE abbr = ? AND num = ?", (abbr, number)).fetchone()
		if courseobj == None:
			self.c.execute("INSERT INTO Courses_Have(abbr, num, name, description, credits, subject) VALUES(?, ?, ?, ?, ?, ?)", (abbr, number, name, description, credits, subject))

	def ensure_instructor(self, instructor):
		instructorobj = self.c.execute("SELECT * FROM Instructors WHERE name = ?", (instructor,)).fetchone()
		if instructorobj == None:
			self.c.execute("INSERT INTO Instructors(name) VALUES(?)", (instructor,))

	def ensure_timeblock(self, day, start_time, end_time):
		timeblockobj = self.c.execute("SELECT * FROM TimeBlocks WHERE day = ? AND start_time = ? AND end_time = ?", (day, start_time, end_time)).fetchone()
		if timeblockobj == None:
			self.c.execute("INSERT INTO TimeBlocks(day, start_time, end_time) VALUES(?, ?, ?)", (day, start_time, end_time))

	def ensure_meetsat(self, CRN, quarter_id, day, start_time, end_time):
		meetsatobj = self.c.execute("SELECT * FROM Meets_At WHERE CRN = ? AND day = ? AND start_time = ? AND end_time = ?", (CRN, day, start_time, end_time)).fetchone()
		if meetsatobj == None:
			self.c.execute("INSERT INTO Meets_At(CRN, offered_in_season, offered_in_type, offered_in_year, day, start_time, end_time) VALUES(?, ?, ?, ?, ?, ?, ?)", (CRN,) + quarter_id + (day, start_time, end_time))

	def ensure_course_offered_in_term(self, subject, num, quarter_id):
		offeredinobj = self.c.execute("""SELECT *
FROM
	Course_Offered_In_Term
WHERE
	subject = ?, num = ?, season = ?, term_type = ?, year = ?""", (subject, num) + quarter_id).fetchone()
		if offeredinobj == None:
			self.c.execute("INSERT INTO Course_Offered_In_Term(subject, num, season, term_type, year) VALUES(?, ?, ?, ?, ?)", (subject, num) + quarter_id)

	def insert_section(self, CRN, section, capacity, enrolled, abbr, course_number, instructor, quarter_id, campus):
		self.c.execute("INSERT INTO Sections(CRN, section_id, capacity, enrolled, instance_of_subject, instance_of_number, taught_by, offered_in_season, offered_in_type, offered_in_year, offered_at) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (CRN, section, capacity, enrolled, abbr, course_number, instructor) + quarter_id + (campus,))

	def get_sections_for_subject_in_term(self, subject, quarter_id, use_abbr = False):
		to_check = "abbr" if use_abbr else "subject"
		return self.c.execute("""SELECT *
FROM
	Courses_Have CH, Sections S
WHERE
	CH.""" + to_check + """ = ? AND CH.abbr = S.instance_of_subject AND
	S.offered_in_season = ? AND S.offered_in_type = ? AND S.offered_in_year = ?""", (subject,) + quarter_id)

	def subject_checked_in_term(self, subject, quarter_id, use_abbr = False):
		return self.get_sections_for_subject_in_term(subject, quarter_id, use_abbr).fetchone() != None

	def get_actual_campus(self, campus):
		try:
			actual_campus = self.campus_map[campus]
		except:
			self.campus_map[campus] = campus
			self.c.execute("INSERT INTO Campuses(name) VALUES(?)", (campus,))
			actual_campus = campus

		return actual_campus

	def sanitize_string(self, s, dirty):
		return s[:-len(dirty)] if s.endswith(dirty) else s

	def get_year_from_quarter(self, quarter):
		if "Fall" in quarter:
			group = 1
		else:
			group = 2
		last_two = re.search("(\d\d)-(\d\d)", quarter).group(group)
		if int(last_two) >= 90:
			return "19" + last_two

		return "20" + last_two

	def ctrl_click(self, link):
		ActionChains(self.driver).key_down(Keys.CONTROL).perform()
		link.click()
		ActionChains(self.driver).key_up(Keys.CONTROL).perform()	

	def setup_checked_quarters(self):
		self.checked_quarters = []
		quartersobj = self.c.execute("SELECT season, term_type, year FROM Terms")
		for quarterobj in quartersobj:
			self.checked_quarters.append(str(quarterobj[0]) + " " + str(quarterobj[1]) + " " + str(quarterobj[2]))

	def quarter_checked(self, quarter):
		return quarter in self.checked_quarters

	def quarter_has_been_checked(self, quarter):
		self.checked_quarters.append(quarter)

	def parse(self):
		return

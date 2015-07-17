#!/usr/bin/python

#import psycopg2
import sys
import sqlite3
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class SiteParser:
	CAMPUS_MAP = {
	                 u"UC": u"University City",
	                 u"BUR": "Burlington County College",
	                 u"SAC": u"Sacramento",
	                 u"CC": u"Center City",
	                 u"ONL": u"Online",
	                 u"PTS": "PTS",
	                 u"University City": u"University City",
	                 u"Burlington County College": u"Burlington County College",
	                 u"Sacramento": u"Sacramento",
	                 u"Center City": u"Center City",
	                 u"Online": u"Online" 
	              }

	def __init__(self, database):
		self.conn = sqlite3.connect(database)
		self.c = self.conn.cursor()
		self.setup_checked_quarters()
		self.driver = webdriver.Firefox()

	def cleanup(self):
		self.driver.close()
		self.conn.close()

#	def ensure_object(self, table, conditions, condition_values, insert, insert_value_names, insert_values):
#		obj = self.c.execute("SELECT * FROM " + table + " WHERE " + conditions, condition_values).fetchone()
#		if obj == None:
#			insert_string = "INSERT INTO " + table + "(" + insert_value_names + ")" + " VALUES(?"
#			for _ in insert_value_names:
#				insert_string += ", ?"
#			insert_string += ")"
#			self.c.execute(insert_string, insert_values)
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

	def ensure_meetsat(self, CRN, day, start_time, end_time):
		meetsatobj = self.c.execute("SELECT * FROM Meets_At WHERE CRN = ? AND day = ? AND start_time = ? AND end_time = ?", (CRN, day, start_time, end_time)).fetchone()
		if meetsatobj == None:
			self.c.execute("INSERT INTO Meets_At(CRN, day, start_time, end_time) VALUES(?, ?, ?, ?)", (CRN, day, start_time, end_time))

	def get_sections_for_subject_in_term(self, subject, quarter_id):
		return self.c.execute("""SELECT *
FROM
	Courses_Have CH, Sections S
WHERE
	CH.subject = ? AND CH.abbr = S.instance_of_subject AND
	S.offered_in_season = ? AND S.offered_in_type = ? AND S.offered_in_year = ?""", (subject,) + quarter_id)
	

	def get_actual_campus(self, campus):
		try:
			actual_campus = self.CAMPUS_MAP[campus]
		except:
			self.CAMPUS_MAP[campus] = campus
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
		return "20" + re.search("(\d\d)-(\d\d)", quarter).group(group)

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

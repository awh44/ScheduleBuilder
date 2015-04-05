#!/usr/bin/python

from selenium import webdriver
import sqlite3

def find_links(driver, href):
	return driver.find_elements_by_xpath("//*[local-name()='a' and contains(@href, '" + href + "')]")

baseURL = "http://catalog.drexel.edu"
extension = "/coursedescriptions/quarter"
fullURL = baseURL + extension 

conn = sqlite3.connect("../data/courses.db")
c = conn.cursor()
c.execute("DELETE FROM subjects")
driver = webdriver.Firefox()

undergradURL = fullURL + "/undergrad/"
driver.get(undergradURL)
links = find_links(driver, extension + "/undergrad/")
for link in links:
	split_string = str(link.text).split("(")
	name = split_string[0].strip()
	abbrev = split_string[1].strip()[:-1].strip()
	c.execute("INSERT INTO subjects VALUES (?, ?)", (abbrev, name))

gradURL = fullURL + "/grad/"
driver.get(gradURL)
links = find_links(driver, extension + "/grad/")
for link in links:
	split_string = str(link.text).split("(")
	name = split_string[0].strip()
	abbrev = split_string[1].strip()[:-1].strip()
	course_obj = c.execute("SELECT * FROM subjects WHERE subj_id = ?", (abbrev,)).fetchone()
	if course_obj == None:
		c.execute("INSERT INTO subjects VALUES (?, ?)", (abbrev, name))

driver.close()

conn.commit()
conn.close()

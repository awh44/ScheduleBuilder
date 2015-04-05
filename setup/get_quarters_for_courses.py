#!/usr/bin/python

import re
import sqlite3
import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

STOP_QUARTER = "Summer Quarter 98-99"

def sanitize_quarter(quarter):
	return quarter[:-len(" (View only)")] if quarter.endswith(" (View only)") else quarter

def get_course_obj(c, abbrev, number):
	return c.execute("SELECT course_id FROM courses WHERE subj_id = ? AND number = ?", (abbrev, number)).fetchone()
 

def check_all_terms(driver, conn):
	global STOP_QUARTER

	#Determine all of the quarters which have already been added to the database
	checked = []
	c = conn.cursor()
	quartersobj = c.execute("SELECT quarter FROM quarters")
	for quarterobj in quartersobj:
		checked.append(str(quarterobj[0]))

	while True:
		dropdown = driver.find_element_by_name("p_term")
		options = dropdown.find_elements_by_tag_name("option")
		for opt in options:
			quarter = sanitize_quarter(str(opt.text))
			if quarter not in checked and quarter != "None" and quarter.find("Semester") == -1:
				c.execute("INSERT INTO quarters(quarter) VALUES(?)", (quarter,))
				checked.append(quarter)
				
				opt.click()
				driver.find_element_by_xpath("//*[@value='Submit']").click()
				check_all_subjects(driver, quarter, c)
				
				#make sure that all of the subjects worked first, then commit them all at once
				conn.commit()

				#then navigate back and do again
				driver.back()
				break
			
			if quarter == STOP_QUARTER:
				return

def check_all_subjects(driver, quarter, c):
	quarter_id = c.execute("SELECT quarter_id FROM quarters WHERE quarter = ?", (quarter,)).fetchone()[0]
	checked = []
	while True:
		subjects = driver.find_elements_by_tag_name("option")
		for sub in subjects:
			#Get the name of the subject
			subj_id = str(sub.get_attribute("value"))
	
			if subj_id not in checked:
				#Note that this subject has now been checked
				checked.append(subj_id)

				#Make sure the subject is in the database, so first select it
				subobj = c.execute("SELECT * FROM subjects WHERE subj_id = ?", (subj_id,)).fetchone()
				if subobj == None:
					print "Couldn't find subject", sub.text, ", inserting now."
					#If the subject could not be found in the database, make sure to insert it
					c.execute("INSERT INTO subjects(subj_id, name) VALUES(?, ?)", (subj_id, sub.text))

				#However, if it could be found, and the subject has not been checked, continue
				#by noting that it's been checked, selecting in the multiselect, and clicking
				sub.click()
				driver.find_element_by_xpath("//*[@value='Course Search']").click()

				#Pull out all of the course numbers
				numbers = driver.find_elements_by_class_name("dddefault")
				for num in numbers:
					if re.match("[0-9]{3}", str(num.text)) != None:
						courseobj = get_course_obj(c, subj_id, num.text)
						#If the course hasn't been seen before, make sure to insert it
						if courseobj == None:
							course_name = num.find_element_by_xpath(".//following-sibling::*[local-name()='td']").text
							c.execute("INSERT INTO courses(subj_id, number, name) VALUES(?, ?, ?)", (subj_id, num.text, course_name))
							courseobj = get_course_obj(c, subj_id, num.text)

						course_id = courseobj[0]
						c.execute("INSERT INTO quarters_for_courses(quarter_id, course_id) VALUES(?, ?)", (quarter_id, course_id))
				
				#Go back for the next subject
				driver.back()
				break
			elif checked[len(checked) - 1] == subj_id:
				#If looking at the previously seen subject, hold control and click it to deselect it
				ActionChains(driver).key_down(Keys.CONTROL).perform()
				sub.click()
				ActionChains(driver).key_up(Keys.CONTROL).perform()
			
			if subj_id == "WRIT":
				return

if len(sys.argv) < 3:
	print "Please include your username and password for one.drexel.edu."
	sys.exit(1)	


driver = webdriver.Firefox()
driver.get("http://one.drexel.edu")

driver.find_element_by_name("username").send_keys(sys.argv[1])
driver.find_element_by_name("password").send_keys(sys.argv[2])
driver.find_element_by_name("submit").click()

driver.find_element_by_xpath("//*[contains(text(),'ACADEMICS')]").find_element_by_xpath("..").click()
driver.find_element_by_xpath("//*[contains(text(), 'Check Course Availability')]").click()
driver.close()
for handle in driver.window_handles:
	driver.switch_to_window(handle)

conn = sqlite3.connect("../data/courses.db")
check_all_terms(driver, conn)
conn.close()

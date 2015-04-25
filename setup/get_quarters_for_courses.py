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
	quartersobj = c.execute("SELECT season, year FROM quarters")
	for quarterobj in quartersobj:
		checked.append(str(quarterobj[0]) + " Quarter " + str(quaterobj[1]))

	while True:
		dropdown = driver.find_element_by_name("p_term")
		options = dropdown.find_elements_by_tag_name("option")
		for opt in options:
			quarter = sanitize_quarter(str(opt.text))
			if quarter not in checked and quarter != "None" and quarter.find("Semester") == -1 and quarter.find("Continuing") == -1:
				checked.append(quarter)
				season, _, year = quarter.split()
				c.execute("INSERT INTO quarters(season, year) VALUES(?, ?)", (season, year))
				
				opt.click()
				driver.find_element_by_xpath("//*[@value='Submit']").click()
				check_all_subjects(driver, c.lastrowid, c)
				
				#make sure that all of the subjects worked first, then commit them all at once
				conn.commit()

				#then navigate back and do again
				driver.back()
				break
			
			if quarter == STOP_QUARTER:
				return

def check_all_subjects(driver, quarter_id, c):
	last_sub_text = driver.find_element_by_xpath("//*[local-name()='option'][last()]").text
	checked = []
	while True:
		subjects = driver.find_elements_by_tag_name("option")
		for sub in subjects:
			#Get the name of the subject
			if sub.get_attribute("value") != None:
				subj_id = str(sub.get_attribute("value"))
				sub_text = sub.text
				if subj_id not in checked and sub_text != "":
					#Note that this subject has now been checked
					checked.append(subj_id)

					#Make sure the subject is in the database, so first select it
					subobj = c.execute("SELECT * FROM subjects WHERE subj_id = ?", (subj_id,)).fetchone()
					if subobj == None:
						print "Couldn't find subject", sub.text, ", inserting now."
						#If the subject could not be found in the database, make sure to insert it
						c.execute("INSERT INTO subjects(subj_id, name) VALUES(?, ?)", (subj_id, sub.text))

					#However, once found or inserted, continue selecting in the multiselect and clicking
					sub.click()
					driver.find_element_by_xpath("//*[@value='Course Search']").click()

					#Pull out all of the course numbers - however, this class also includes other elements on the page
					#numbers = driver.find_elements_by_class_name("dddefault")
					#for num in numbers:
						#Because the CSS class also includes other elements on the page, make sure the inner text is a course number
					#	if re.match("[0-9]{3}", str(num.text)) != None:
					#		courseobj = get_course_obj(c, subj_id, num.text)
					#		#If the course hasn't been seen before, make sure to insert it
					#		if courseobj == None:
					#			course_name = num.find_element_by_xpath(".//following-sibling::*[local-name()='td']").text
					#			c.execute("INSERT INTO courses(subj_id, number, name) VALUES(?, ?, ?)", (subj_id, num.text, course_name))
					#			courseobj = get_course_obj(c, subj_id, num.text)

					#		course_id = courseobj[0]
					#		c.execute("INSERT INTO course_quarter_map(course_id, quarter_id) VALUES(?, ?)", (course_id, quarter_id))
					#		check_detailed_course_data(driver, num, c.lastrowid, c)
					
					#Go back for the next subject
					driver.back()
					break
				elif checked[len(checked) - 1] == subj_id:
					#If looking at the previously seen subject, hold control and click it to deselect it
					ActionChains(driver).key_down(Keys.CONTROL).perform()
					sub.click()
					ActionChains(driver).key_up(Keys.CONTROL).perform()
			
				if sub_text == last_sub_text:
					return

def check_all_courses(driver, subj_id, c):
	last_num_text = driver.find_element_by_xpath("//*[contains(@class, 'dddefault')][last()]").text
	checked = []
	while True:
		numbers = driver.find_elements_by_class_name("dddefault")
		for num in numbers:
			checked.append(num.text)
			#Because the CSS class also includes other elements on the page, make sure the inner text is a course number
			if num.text not in checked and re.match("[0-9]{3}", str(num.text)) != None:
				courseobj = get_course_obj(c, subj_id, num.text)
				#If the course hasn't been seen before, make sure to insert it
				if courseobj == None:
					course_name = num.find_element_by_xpath(".//following-sibling::*[local-name()='td']").text
					c.execute("INSERT INTO courses(subj_id, number, name) VALUES(?, ?, ?)", (subj_id, num.text, course_name))
					courseobj = get_course_obj(c, subj_id, num.text)

				course_id = courseobj[0]
				c.execute("INSERT INTO course_quarter_map(course_id, quarter_id) VALUES(?, ?)", (course_id, quarter_id))
#				driver.back()
				break
			
			if num.text == last_num_text:
				return


def check_detailed_course_data(driver, num_element, course_quarter_id, c):
	form_element = num_element.find_element_by_xpath(".//following-sibling::*[local-name()='td']/*[local-name()='form']")
	form_element.submit()
	print "course_quarter_id =", course_quarter_id
	driver.back()
	

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

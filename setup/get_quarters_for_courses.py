#!/usr/bin/python

import re
import sqlite3
import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

DAYS_OF_THE_WEEK = { u"S": 0, u"M": 1, u"T": 2, u"W": 3, u"R": 4, u"F": 5 }
STOP_QUARTER = "Summer Quarter 14-15"
#STOP_QUARTER = "Summer Quarter 98-99"

def sanitize_string(s, dirty):
	return s[:-len(dirty)] if s.endswith(dirty) else s	

def sanitize_quarter(quarter):
	return sanitize_string(quarter, " (View only)")

def sanitize_instructor(instructor):
	return sanitize_string(instructor, " (P)")

def convert_ampm_24hour(time):
	if time.find("pm") >= 0:
		time = sanitize_string(time, " pm")
		hours, minutes = time.split(":")
		hoursInt = int(hours)
		if hoursInt != 12:
			hoursInt += 12
			
		return 60 * hoursInt + int(minutes)

	time = sanitize_string(time, " am")
	hours, minutes = time.split(":")
	hoursInt = int(hours)
	if hoursInt == 12:
		hoursInt = 0
	
	return 60 * hoursInt + int(minutes)
		

def get_course_obj(c, abbrev, number):
	return c.execute("SELECT course_id FROM courses WHERE subj_id = ? AND number = ?", (abbrev, number)).fetchone() 

def check_all_terms(driver, conn):
	global STOP_QUARTER

	#Determine all of the quarters which have already been added to the database
	checked = []
	c = conn.cursor()
	quartersobj = c.execute("SELECT season, year FROM quarters")
	for quarterobj in quartersobj:
		checked.append(str(quarterobj[0]) + " Quarter " + str(quarterobj[1]))

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
	last_sub_text = "Anthropology" #driver.find_element_by_xpath("//*[local-name()='option'][last()]").text
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
						print "Couldn't find subject " + sub.text + "; inserting now."
						#If the subject could not be found in the database, make sure to insert it
						c.execute("INSERT INTO subjects(subj_id, name) VALUES(?, ?)", (subj_id, sub.text))

					#However, once found or inserted, continue selecting in the multiselect and clicking
					sub.click()
					driver.find_element_by_xpath("//*[@value='Course Search']").click()
					check_all_courses(driver, subj_id, quarter_id, c)
										
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

def check_all_courses(driver, subj_id, quarter_id, c):
	goal = len(driver.find_elements_by_class_name("dddefault")) / 2
	checked = []
	while True:
		numbers = driver.find_elements_by_class_name("dddefault")
		for num in numbers:
			#Because the CSS class also includes other elements on the page, make sure the inner text is a course number
			if re.match("[0-9]{3}", str(num.text)) != None and num.text not in checked:
				checked.append(num.text)
				courseobj = get_course_obj(c, subj_id, num.text)
				#If the course hasn't been seen before, make sure to insert it
				if courseobj == None:
					course_name = num.find_element_by_xpath(".//following-sibling::*[local-name()='td']").text
					c.execute("INSERT INTO courses(subj_id, number, name) VALUES(?, ?, ?)", (subj_id, num.text, course_name))
					courseobj = get_course_obj(c, subj_id, num.text)

				course_id = courseobj[0]
				c.execute("INSERT INTO course_quarter_map(course_id, quarter_id) VALUES(?, ?)", (course_id, quarter_id))
				course_quarter_id = c.lastrowid
								
				num.find_element_by_xpath(".//following-sibling::*[local-name()='td']/*[local-name()='form']//*[local-name()='input' and @name='SUB_BTN']").click()
				credits = check_detailed_course_data(driver, course_quarter_id, c)
				driver.back()
				if len(checked) == goal:
					return

				break

def check_detailed_course_data(driver, course_quarter_id, c):
	global DAYS_OF_THE_WEEK

	table = driver.find_element_by_xpath("//*[local-name()='table' and contains(@class, 'datadisplaytable')]")
	course_rows = table.find_elements_by_xpath(".//*[local-name()='tr' and ./*[local-name()='td'][2]/*[local-name()='a']]")
	for row in course_rows:
		instructor = sanitize_instructor(row.find_element_by_xpath(".//*[local-name()='td'][20]").text)
		c.execute("INSERT INTO instructors(name) VALUES(?)", (instructor,))
		instructor_id = c.lastrowid

		CRN = row.find_element_by_xpath(".//*[local-name()='td'][2]/*[local-name()='a']").text
		section = row.find_element_by_xpath(".//*[local-name()='td'][5]").text
		campus = row.find_element_by_xpath(".//*[local-name()='td'][6]").text
		capacity = row.find_element_by_xpath(".//*[local-name()='td'][11]").text
		taken = row.find_element_by_xpath(".//*[local-name()='td'][12]").text

		c.execute("INSERT INTO course_instances(course_quarter_id, CRN, section, campus, capacity, taken, instructor_id) VALUES(?, ?, ?, ?, ?, ?, ?)", (course_quarter_id, CRN, section, campus, capacity, taken, instructor_id))
		instance_id = c.lastrowid
	
		day_rows_path = "//*[local-name()='tr' and not(./*[local-name()='td'][2]/*[local-name()='a']) and not(@align)][preceding-sibling::*[local-name()='tr' and contains(., 'NR')][1][contains(., '" + CRN + "')]] | //*[local-name()='tr' and ./*[local-name()='td'][2]/*[local-name()='a' and contains(., '" + CRN + "')]]"
		day_rows = row.find_elements_by_xpath(day_rows_path)
		days = { u"S": [], u"M": [], u"T": [], u"W": [], u"R": [], u"F": [] }
		for day_row in day_rows:
			days_of_week = day_row.find_element_by_xpath(".//*[local-name()='td'][9]").text.strip()
			#if days_of_week is u"", it usually means that it's an online class - don't need to know times
			if days_of_week != u"":
				dates = row.find_element_by_xpath(".//*[local-name()='td'][21]").text.strip()
				if dates.find("-") > 0:
					start_date, end_date = dates.split("-")
					#Going to assume that instances with the same start and end date are the final.
					#This does NOT appear to always be the case, but it's the best that can be done
					#it seems
					if start_date != end_date:
						full_time = row.find_element_by_xpath(".//*[local-name()='td'][10]").text.strip()
						if full_time != "TBA":
							start_time, end_time = full_time.split("-")
						else:
							start_time = end_time = "TBA"
						for day_of_week in days_of_week:
							c.execute("INSERT INTO instance_time_map(instance_id, day_id, start, end) VALUES(?, ?, ?, ?)", (instance_id, DAYS_OF_THE_WEEK[day_of_week], convert_ampm_24hour(start_time), convert_ampm_24hour(end_time)))
				else:
					print "Could not find start and end dates:", dates
			
	return credits

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

conn = sqlite3.connect("../data/new_courses.db")
check_all_terms(driver, conn)
conn.close()

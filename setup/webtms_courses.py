#!/usr/bin/python

import sqlite3
import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

DAYS_OF_THE_WEEK = { u"S": 0, u"M": 1, u"T": 2, u"W": 3, u"R": 4, u"F": 5 }
CAMPUSES = { u"UC": 1, u"University City": 1, u"Online": 2, u"ONL": 2, u"Burlington County College":
3, u"BCC": 3, "Off Campus": 4 }
COURSE_ROWS_XPATH = "//*[local-name()='tr' and contains(@class, 'tableHeader')]/following-sibling::*[local-name()='tr' and (@class='even' or @class='odd')]"

def sanitize_string(s, dirty):
    return s[:-len(dirty)] if s.endswith(dirty) else s

def get_instructor_id(instructor, c):
	obj = c.execute("SELECT instructor_id FROM instructors WHERE name = ?", (instructor,)).fetchone()
	if obj != None:
		return obj[0]
	
	c.execute("INSERT INTO instructors(name) VALUES(?)", (instructor,))
	return c.lastrowid

def get_value_from_label(driver, label):
	return driver.find_element_by_xpath("//*[local-name()='td' and contains(@class, 'tableHeader') and .='" + label + "']/following-sibling::*").text

def refocus_current_tab(driver):
	driver.switch_to_window(driver.current_window_handle)

def open_link_in_new_tab(driver, link):
	ActionChains(driver).key_down(Keys.CONTROL).perform()
	link.click()
	ActionChains(driver).key_up(Keys.CONTROL).perform()
	driver.find_element_by_tag_name("body").send_keys(Keys.CONTROL + Keys.TAB)
	refocus_current_tab(driver)
	
def close_tab(driver):
	driver.find_element_by_tag_name("body").send_keys(Keys.CONTROL + "w")
	refocus_current_tab(driver)

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

def check_all_quarters(driver, conn):
	checked = []
	c = conn.cursor()
	quartersobj = c.execute("SELECT season, year FROM quarters")
	for quarterobj in quartersobj:
		checked.append(str(quarterobj[0]) + " Quarter " + str(quarterobj[1]))

	quarter_links = driver.find_elements_by_xpath("//*[local-name()='td' and text()='Quarter Term Courses']//ancestor::*[local-name()='table'][1]//*[local-name()='a']")
	for link in quarter_links:
		if link.text not in checked:
			season, _, year = link.text.split()
			c.execute("INSERT INTO quarters(season, year) VALUES(?, ?)", (season, year))

			open_link_in_new_tab(driver, link)
			check_all_subjects(driver, c.lastrowid, c)

			#make sure that all of the subjects worked first, then commit them all at once
			conn.commit()

			close_tab(driver)

def check_all_subjects(driver, quarter_id, c):
	colleges = driver.find_elements_by_xpath("//*[local-name()='div' and @id='sideLeft']//*[local-name()='a']")
	for college in colleges:
		open_link_in_new_tab(driver, college)
		subjects = driver.find_elements_by_xpath("//*[local-name()='table' and @class='collegePanel']//*[local-name()='a']")
		for subject in subjects:
			subject_name = subject.text
			open_link_in_new_tab(driver, subject)
			check_all_courses(driver, subject_name, quarter_id, c)
			close_tab(driver)

		close_tab(driver)

def check_all_courses(driver, subject, quarter_id, c):
	global COURSE_ROWS_XPATH
	courses = driver.find_elements_by_xpath(COURSE_ROWS_XPATH)
	subj_id = courses[0].find_element_by_xpath("./*[local-name()='td'][1]").text
	subobj = c.execute("SELECT * FROM subjects WHERE subj_id = ?", (subj_id,)).fetchone()
	if subobj == None:
		print "Couldn't find subject " + subject + "; inserting now."
		#If the subject could not be found in the database, make sure to insert it
		c.execute("INSERT INTO subjects(subj_id, name) VALUES(?, ?)", (subj_id, subject))

	checked = []
	for course in courses:
		number = course.find_element_by_xpath(".//*[local-name()='td'][2]").text
		if number not in checked:
			checked.append(number)
			courseobj = c.execute("SELECT course_id FROM courses WHERE subj_id = ? AND number = ?", (subj_id, number)).fetchone()
			if courseobj != None:
				course_id = courseobj[0]
			else:
				#If the course hasn't been seen before, make sure to insert it
				name = course.find_element_by_xpath(".//*[local-name()='td'][7]").text
				c.execute("INSERT INTO courses(subj_id, number, name) VALUES(?, ?, ?)", (subj_id, number, name))
				course_id = c.lastrowid
			c.execute("INSERT INTO course_quarter_map(course_id, quarter_id) VALUES(?, ?)", (course_id, quarter_id))
			check_detailed_course_data(driver, number, c.lastrowid, c)

def check_detailed_course_data(driver, number, course_quarter_id, c):
	global COURSE_ROWS_XPATH
	instances = driver.find_elements_by_xpath(COURSE_ROWS_XPATH + "[./*[local-name()='td'][2][contains(., '" + number + "')]]")
	for instance in instances:		
		CRN_element = instance.find_element_by_xpath("./*[local-name()='td'][6]//*[local-name()='a']")
		CRN = CRN_element.text	
		open_link_in_new_tab(driver, CRN_element)
		instructor = get_value_from_label(driver, "Instructor(s)")
		instructor_id = get_instructor_id(instructor, c)

		section = get_value_from_label(driver, "Section")
		campus = CAMPUSES[get_value_from_label(driver, "Campus")]
		capacity = get_value_from_label(driver, "Max Enroll")
		taken = get_value_from_label(driver, "Enroll")
		if taken == "CLOSED":
			taken = capacity

		c.execute("INSERT INTO course_instances(course_quarter_id, CRN, section, campus_id, capacity, taken, instructor_id) VALUES(?, ?, ?, ?, ?, ?, ?)", (course_quarter_id, CRN, section, campus, capacity, taken, instructor_id))
		
		instance_id = c.lastrowid

		times = driver.find_elements_by_xpath("//*[local-name()='tr' and contains(@class, 'tableHeader') and contains(., 'Times')]//following-sibling::*[local-name()='tr' and (contains(@class, 'even') or contains(@class, 'odd')) and not(contains(., 'Final Exam'))]")
		for time in times:
			time_string = time.find_element_by_xpath(".//*[local-name()='td'][3]").text
			if time_string.find("-") > 0:	
				start, end = time_string.split(" - ")
				startInt = convert_ampm_24hour(start)
				endInt = convert_ampm_24hour(end)
				days = time.find_element_by_xpath(".//*[local-name()='td'][4]").text
				for day in days:
					day_id = DAYS_OF_THE_WEEK[day]
				c.execute("INSERT INTO instance_time_map(instance_id, day_id, start, end) VALUES(?, ?, ?, ?)", (instance_id, day_id, startInt, endInt))
			
			
		close_tab(driver)
			

def main():
	driver = webdriver.Firefox()
	driver.get("http://drexel.edu/webtms")
	
	conn = sqlite3.connect("../data/new_courses.db")
	check_all_quarters(driver, conn)
	conn.close()

	driver.close()
	sys.exit(0)

if __name__ == "__main__":
	main()

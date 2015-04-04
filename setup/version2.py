#!/usr/bin/python
import sys
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def check_all_terms(driver):
	classes = {}
	checked = []
	while True:
		dropdown = driver.find_element_by_name("p_term")
		options = dropdown.find_elements_by_tag_name("option")
		for opt in options:
			quarter = str(opt.text)
			if quarter not in checked and quarter != "None" and quarter.find("Semester") == -1:
				checked.append(quarter)
				quarter = quarter
				if quarter.endswith(" (View only)"):
					quarter = quarter[:-len(" (View only)")]
				opt.click()
				driver.find_element_by_xpath("//*[@value='Submit']").click()
				check_all_subjects(driver, classes, quarter)
				driver.back()
				break
			
			if quarter == "Summer Quarter 98-99 (View only)":
				return classes

def check_all_subjects(driver, classes, quarter):
	checked = []
	while True:
		subjects = driver.find_elements_by_tag_name("option")
		for sub in subjects:
			textval = sub.text
			if textval not in checked:
				checked.append(textval)
				sub.click()
				driver.find_element_by_xpath("//*[@value='Course Search']").click()
				numbers = driver.find_elements_by_class_name("dddefault")
				for num in numbers:
					if re.match("[0-9]{3}", str(num.text)) != None:
						deptPlusNum = textval + " " + num.text
						if deptPlusNum in classes:
							classes[deptPlusNum] += [quarter]
						else:
							classes[deptPlusNum] = [quarter]
				driver.back()
				break
			elif checked[len(checked) - 1] == textval:
				ActionChains(driver).key_down(Keys.CONTROL).perform()
				sub.click()
				ActionChains(driver).key_up(Keys.CONTROL).perform()
			
			if textval == "Writing":
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

classes = check_all_terms(driver)
fout = open("coursedata", "w")
for course in sorted(classes.keys()):
	fout.write(course + " | ")
	for quarter in classes[course]:
		fout.write(quarter + " | ")
	fout.write("\n")
fout.close()

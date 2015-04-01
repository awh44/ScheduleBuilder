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
			if opt.text not in checked and opt.text != "None" and str(opt.text).find("Semester") == -1:
				checked.append(opt.text)
				quarter = str(opt.text)
				if quarter.endswith(" (View only)"):
					quarter = quarter[:-len(" (View only)")]
				opt.click()
				driver.find_element_by_xpath("//*[@value='Submit']").click()
				for handle in driver.window_handles:
					driver.switch_to_window(handle)
				check_all_subjects(driver, classes, quarter)
				print classes
				driver.back()
				break

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
			
			if textval == "Animation":#Writing":
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

check_all_terms(driver)

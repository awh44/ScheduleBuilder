#!/usr/bin/python

from SiteParser import SiteParser

from selenium.webdriver.common.keys import Keys

class TMSParser(SiteParser):
	def press_with_ctrl(self, key):
		self.driver.find_element_by_tag_name("body").send_keys(Keys.CONTROL + key)
		
	def refocus_current_tab(self):
		self.driver.switch_to_window(self.driver.current_window_handle)

	def open_link_in_new_tab(self, link):
		self.ctrl_click(link)
		self.press_with_ctrl(Keys.TAB)
		self.refocus_current_tab()

	def close_tab(self):
		self.press_with_ctrl("w")
		self.refocus_current_tab()

	def get_value_from_label(self, label):	
		return self.driver.find_element_by_xpath("//*[local-name()='td' and contains(@class, 'tableHeader') and .='" + label + "']/following-sibling::*").text

	def remove_credits(self, credits):
		if " " in credits:
			return credits.split(" ")[1]

		return "0.0"
		
	def parse(self):
		SiteParser.parse(self)
		self.driver.get("https://drexel.edu/webtms")
		self.check_all_quarters();
		self.cleanup()
	
	def check_all_quarters(self):
		quarter_links = self.driver.find_elements_by_xpath("//*[local-name()='td' and contains(text(), 'Term Courses')]//ancestor::*[local-name()='table'][1]//*[local-name()='a' and not(contains(., '15-16'))]")
		for link in quarter_links:
			#if not self.quarter_checked(link.text):
			quarter = link.text
			season, term_type, _ = quarter.split()
			year = self.get_year_from_quarter(quarter)
			quarter_id = (season, term_type, year)
			self.ensure_quarter(quarter_id)
			self.open_link_in_new_tab(link)
			self.check_all_subjects(quarter_id)
			self.close_tab()
				
	def check_all_subjects(self, quarter_id):
		colleges = self.driver.find_elements_by_xpath("//*[local-name()='div' and @id='sideLeft']//*[local-name()='a']")
		for college in colleges:
			self.open_link_in_new_tab(college)
			subjects = self.driver.find_elements_by_xpath("//*[local-name()='table' and @class='collegePanel']//*[local-name()='a']")
			for subject in subjects:
				subject_name = subject.text
				if self.get_sections_for_subject_in_term(subject_name, quarter_id).fetchone() == None:
					self.ensure_subject(subject_name)
					self.open_link_in_new_tab(subject)
					self.check_all_courses(subject_name, quarter_id)
					self.close_tab()
					self.conn.commit()
			self.close_tab()

	def check_all_courses(self, subject_name, quarter_id):
		sections = self.driver.find_elements_by_xpath("//*[local-name()='tr' and contains(@class, 'tableHeader')]/following-sibling::*[local-name()='tr' and (@class='even' or @class='odd')]")
		abbr = sections[0].find_element_by_xpath("./*[local-name()='td'][1]").text
		self.check_all_sections(sections, abbr, subject_name, quarter_id)

	def check_all_sections(self, sections, abbr, subject_name, quarter_id):
		for section in sections:
			CRN_element = section.find_element_by_xpath("./*[local-name()='td'][6]//*[local-name()='a']")
			CRN = CRN_element.text
			
			self.open_link_in_new_tab(CRN_element)

			course_number = self.get_value_from_label("Course Number")
			course_desc = self.driver.find_element_by_xpath("//*[local-name()='div' and @class='courseDesc']").text
			course_name = self.get_value_from_label("Title")
			credits = self.remove_credits(self.driver.find_element_by_xpath("//*[local-name()='div' and contains(@class, 'subpoint') and contains(., 'Credits')]").text)
			instructor = self.get_value_from_label("Instructor(s)")
			section = self.get_value_from_label("Section")
			campus = self.get_value_from_label("Campus")
			capacity = self.get_value_from_label("Max Enroll")
			enrolled = self.get_value_from_label("Enroll")
			if enrolled == "CLOSED":
				enrolled = capacity

			self.ensure_course(abbr, course_number, course_name, course_desc, credits, subject_name)
			self.ensure_instructor(instructor)
			campus = self.get_actual_campus(campus)

			self.c.execute("INSERT INTO Sections(CRN, section_id, capacity, enrolled, instance_of_subject, instance_of_number, taught_by, offered_in_season, offered_in_type, offered_in_year, offered_at) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (CRN, section, capacity, enrolled, abbr, course_number, instructor) + quarter_id + (campus,))
			self.check_all_times_for_section(CRN)
			self.close_tab()

	def check_all_times_for_section(self, CRN):
		times = self.driver.find_elements_by_xpath("//*[local-name()='tr' and contains(@class, 'tableHeader') and contains(., 'Times')]//following-sibling::*[local-name()='tr' and (contains(@class, 'even') or contains(@class, 'odd')) and not(contains(., 'Final Exam'))]")
		for time in times:
			time_string = time.find_element_by_xpath(".//*[local-name()='td'][3]").text
			if time_string.find("-") > 0:
				start, end = time_string.split(" - ")
				days = time.find_element_by_xpath(".//*[local-name()='td'][4]").text
				for day in days:
					self.ensure_timeblock(day, start, end)
					self.ensure_meetsat(CRN, day, start, end)

#!/usr/bin/python

from SiteParser import SiteParser

class DrexelOneParser(SiteParser):
	STOP_QUARTER = "Summer Quarter 98-99"
	SUBJECTS_XPATH = "//*[local-name()='select' and @id='subj_id']/*[local-name()='option']"
	COURSE_NUMBERS_XPATH = "//*[@class='dddefault']"
	CRN_XPATH = "./*[local-name()='td'][2]/*[local-name()='a']" 
	
	def __init__(self, database, username, password):
		SiteParser.__init__(self, database)
		self.username = username
		self.password = password

	def sanitize_quarter(self, quarter):
		return self.sanitize_string(quarter, " (View only)")

	def sanitize_instructor(self, instructor):
		return self.sanitize_string(instructor, " (P)")

	def switch_window(self):
		self.driver.close()
		for handle in self.driver.window_handles:
			self.driver.switch_to_window(handle)
	
	def get_last_text(self, xpath):
		return self.driver.find_element_by_xpath(xpath + "[last()]").text

	def ensure_subject_by_abbr(self, subject, abbr):
		subjectobj = self.c.execute("SELECT * FROM Courses WHERE abbr = ?", (abbr,)).fetchone()
		if subjectobj == None:
			self.c.execute("INSERT INTO Subjects(name) VALUES(?)", (subject,))

	def parse(self):
		SiteParser.parse(self)
		self.driver.get("http://one.drexel.edu")
		self.log_in()
		self.navigate_to_terms()
		self.check_all_terms()
		self.cleanup()

	def log_in(self):
		self.driver.find_element_by_name("username").send_keys(self.username)
		self.driver.find_element_by_name("password").send_keys(self.password)
		self.driver.find_element_by_name("submit").click()

	def navigate_to_terms(self):
		self.driver.find_element_by_xpath("//*[contains(text(),'ACADEMICS')]").find_element_by_xpath("..").click()
		self.driver.find_element_by_xpath("//*[contains(text(), 'Check Course Availability')]").click()	
		self.switch_window()

	def check_all_terms(self):
		index = 0
		while True:
			dropdown = self.driver.find_element_by_name("p_term")
			options = dropdown.find_elements_by_xpath(".//*[local-name()='option' and not(contains(., 'None') or contains(., 'Continuing'))]")
			opt = options[index]
			quarter = self.sanitize_quarter(opt.text)
			season, term_type, _ = quarter.split()
			year = self.get_year_from_term(quarter)
			quarter_id = (season, term_type, year)
			self.ensure_quarter(quarter_id)

			opt.click()
			self.driver.find_element_by_xpath("//*[@value='Submit']").click()
			self.check_all_subjects(quarter_id)

			self.driver.back()

			if quarter == self.STOP_QUARTER:
				return

	def check_all_subjects(self, quarter_id):
		last_sub_text = self.get_last_text(self.SUBJECTS_XPATH)
		index = 0
		while True:
			subjects = self.driver.find_elements_by_tag_name("//*[local-name()='select' and @id='subj_id']/*[local-name()='option']")
			sub = subjects[index]
			#Get the name and the abbreviation of the subject
			subject_name = sub.text
			abbr = str(sub.get_attribute("value"))
			if not self.subject_checked_in_term(abbr, quarter_id, True):
				#Deselect the previous subject
				if index != 0:
					self.ctrl_click(subjects[index - 1])

				#Make sure the subject is in the database
				self.ensure_subject_by_abbr(subject_name, abbr)

				#Once inserted, continue selecting in the multiselect and clicking
				sub.click()
				self.driver.find_element_by_xpath("//*[@value='Course Search']").click()
				self.check_all_courses(abbr, subject_name, quarter_id)
									
				#Go back for the next subject
				self.driver.back()

				#Commit the information for the current subject
				self.conn.commit()
			
			index += 1
			if subject_name == last_sub_text:
				return

	def check_all_courses(self, abbr, subject_name, quarter_id):
		last_num_text = self.get_last_text(self.COURSE_NUMBERS_XPATH)
		index = 0
		while True:
			numbers = self.driver.find_elements_by_xpath("//*[@class='dddefault' and @width='10%']")
			num = numbers[index]
			course_name = num.find_element_by_xpath(".//following-sibling::*[local-name()='td']").text
							
			num.find_element_by_xpath(".//following-sibling::*[local-name()='td']/*[local-name()='form']//*[local-name()='input' and @name='SUB_BTN']").click()
			self.check_all_sections(abbr, num.text, subject_name, course_name, quarter_id)
			self.driver.back()

			index += 1
			if num.text == last_num_text:
				return

	def check_all_sections(self, abbr, num, subject_name, course_name, quarter_id):
		try:
			table = self.driver.find_element_by_xpath("//*[local-name()='table' and contains(@class, 'datadisplaytable')]")
		except:
			self.ensure_course(abbr, num, course_name, None, None, subject_name)
			print "No instances for course."
		return

		#The actual course rows are the ones which have the CRN links
		course_rows = table.find_elements_by_xpath(".//*[local-name()='tr' and not(./*[local-name()='th'])]")
		for row in course_rows:
			try:
				CRN_element = row.find_element_by_xpath(self.CRN_XPATH)
				found = True
			except:
				found = False

			if found:
				try:	
					credits = row.find_element_by_xpath(".//*[local-name()='td'][7]").text
				except:
					credits = None
				
				self.ensure_course(abbr, num, course_name, None, credits, subject_name)
				
				instructor = sanitize_instructor(row.find_element_by_xpath(".//*[local-name()='td'][20]").text)
				self.ensure_instructor(instructor)
				CRN = CRN_element.text
				section = row.find_element_by_xpath(".//*[local-name()='td'][5]").text
				campus = self.get_actual_campus(row.find_element_by_xpath(".//*[local-name()='td'][6]").text)
				capacity = row.find_element_by_xpath(".//*[local-name()='td'][11]").text
				enrolled = row.find_element_by_xpath(".//*[local-name()='td'][12]").text
				self.insert_section(CRN, section, capacity, enrolled, abbr, course_number, instructor, quarter_id, campus)
					
			else:
				self.ensure_times_for_section(CRN, quarter_id, row)

	def check_all_times_for_section(self, CRN, quarter_id, day_row):
		try:
			days_of_week = day_row.find_element_by_xpath(".//*[local-name()='td'][9]").text.strip()
		except:
			#Doesn't actually contain day of the week information - something like waitlist capabilities or "meets with" information
			return

		#if days_of_week is u"", it usually means that it's an online class - don't need to know times
		if days_of_week != u"":
			dates = day_row.find_element_by_xpath(".//*[local-name()='td'][21]").text.strip()
			if "-" in dates:
				start_date, end_date = dates.split("-")
				#Going to assume that instances with the same start and end date are the final.
				#This does NOT appear to always be the case, but it's the best that can be done
				#it seems
				if start_date != end_date:
					time = day_row.find_element_by_xpath(".//*[local-name()='td'][10]").text.strip()
					if "-" in time:
						start, end = time.split("-")
						for day_of_week in days_of_week:
							self.ensure_timeblock(day_of_week, start, end)
							self.ensure_meetsat(CRN, day, start, end)

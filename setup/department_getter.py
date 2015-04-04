#!/usr/bin/python

from selenium import webdriver
import sqlite3

driver = webdriver.Firefox()
driver.get("http://catalog.drexel.edu/coursedescriptions/quarter/undergrad/")

conn = sqlite3.connect("../data/courses.db")
c = conn.cursor()
links = driver.find_elements_by_xpath("//*[local-name()='a' and contains(@href, '/coursedescriptions/quarter/undergrad/')]")
for link in links:
	split_string = str(link.text).split("(")
	name = split_string[0].strip()
	abbrev = split_string[1].strip()[:-1].strip()
	c.execute("INSERT INTO departments VALUES (?, ?)", (abbrev, name))

conn.commit()
conn.close()

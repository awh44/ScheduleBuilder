DROP TABLE Subjects;
DROP TABLE Courses_Have;
DROP TABLE Sections;
DROP TABLE Instructors;
DROP TABLE Campuses;
DROP TABLE Terms;
DROP TABLE TimeBlocks;
DROP TABLE Meets_At;

CREATE TABLE Subjects
(
	name text PRIMARY KEY
);

CREATE TABLE Courses_Have
(
	abbr text,
	num integer,
	name text,
	description text,
	credits real,
	subject text not NULL,
	PRIMARY KEY (abbr, num),
	FOREIGN KEY (subject) REFERENCES Subjects(name)
);

CREATE TABLE Sections
(
	CRN integer,
	offered_in_season text not NULL,
	offered_in_type text not NULL,
	offered_in_year integer not NULL,
	section_id text,
	capacity integer,
	enrolled integer,
	instance_of_subject not NULL,
	instance_of_number not NULL,
	taught_by text not NULL,
	offered_at text not NULL,
	PRIMARY KEY (CRN, offered_in_season, offered_in_type, offered_in_year),
	FOREIGN KEY (instance_of_subject, instance_of_number) REFERENCES Courses_Have(instance_of_subject, instance_of_number),
	FOREIGN KEY (taught_by) REFERENCES Instructors(name),
	FOREIGN KEY (offered_in_year, offered_in_season, offered_in_type) REFERENCES Terms(year, season, term_type),
	FOREIGN KEY (offered_at) REFERENCES Campuses(name)
);

CREATE TABLE Instructors
(
	name text PRIMARY KEY
);

CREATE TABLE Terms
(
	season text,
	term_type text,
	year integer,
	PRIMARY KEY (season, term_type, year)
);

CREATE TABLE Campuses
(
	name text PRIMARY KEY
);

INSERT INTO Campuses(name) VALUES("University City");
INSERT INTO Campuses(name) VALUES("Burlington County College");
INSERT INTO Campuses(name) VALUES("Sacramento");
INSERT INTO Campuses(name) VALUES("Center City");
INSERT INTO Campuses(name) VALUES("Online");
INSERT INTO Campuses(name) VALUES("PTS");

CREATE TABLE TimeBlocks
(
	day text,
	start_time text,
	end_time text,
	PRIMARY KEY (day, start_time, end_time)
);

CREATE TABLE Meets_At
(
	CRN integer,
	offered_in_season text,
	offered_in_type text,
	offered_in_year integer,
	day text,
	start_time text,
	end_time text,
	PRIMARY KEY (CRN, day, start_time, end_time),
	FOREIGN KEY (CRN, offered_in_season, offered_in_type, offered_in_year) REFERENCES Sections (CRN, offered_in_season, offered_in_type, offered_in_year),
	FOREIGN KEY (day, start_time, end_time) REFERENCES TimeBlocks (day, start_time, end_time)
);

ScheduleBuilder
===============

This repository contains code to help with the creation of a master schedule of Drexel University's courses since summer 1998, one which
will, hopefully, present the information in a more elegant way than Drexel's official schedule. Right now, the main feature of the main
application is to let students determine which term during the year a course tends to be offered, a useful fact to know when building plans
of study.

As for code, first, the repository contains, under the setup/ directory, files which create a SQLite database to house all of the coursee
information. The create\_db.py script simply creates the necessary tables and columns in the database. However, get\_quarters\_for\_courses.py
actually logs onto Drexel's student website, one.drexel.edu, using selenium and Firefox, and it navigates the pages and directly pulls
information off the screen, inserting it directly into the SQLite database. The database is stored at data/courses.db. Note that data/
also contains some other, older iterations of the database at any given time as well.

Finally, the repository contains HTML, PHP, and JavaScript files that are to be used as a website for inspection into the database. Currently, the main web page,
as noted above, simply provides dropdowns that let one determine which quarters a course is generally offered. However, in the future,
as new iterations of the database are created, hopefully the website's reach will extend to other functionality. Note that, due to SQLite support issues, this web page is not actually available to view anywhere yet.

ScheduleBuilder
===============

This repository contains code to help with the creation of a master schedule of Drexel University's courses since summer 1998, one which
will, hopefully, present the information in a more elegant way than Drexel's official schedule. Right now, the main feature of the main
application is to let students determine which term during the year a course tends to be offered, a useful fact to know when building plans
of study. The website can be found [here](https://www.cs.drexel.edu/~awh44/schedule/schedule.php).

As for code, first, the repository contains, under the setup/ directory, files which create a SQLite database to house all of the coursee
information. The create\_db.py script simply creates the necessary tables and columns in the database. However, get\_quarters\_for\_courses.py
actually logs onto Drexel's student website, one.drexel.edu, using selenium and Firefox, and it navigates the pages and directly pulls
information off the screen, inserting it directly into the SQLite database. The database is stored at data/courses.db. Note that data/
also contains some other, older iterations of the database at any given time as well.

Finally, the repository contains HTML, PHP, Python and JavaScript files that are to be used as a website for inspection into the database. (Please do not judge the strange mixture of PHP and Python scripts. The computer science department's web server does not support the PHP SQLite package, so PHP cannot be used for the server-side scripting. It also does not support a cgi-bin, so Python cannot be used for the server-side scripting. Hence, the PHP is called from the JavaScript, which in turn calls the Python for the SQLite support.) Currently, the main web page,
as noted above, simply provides dropdowns that let one determine which quarters a course is generally offered. However, in the future,
as new iterations of the database are created, hopefully the website's reach will extend to other functionality.

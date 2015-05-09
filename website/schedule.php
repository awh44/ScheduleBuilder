<html>
<head>
	<title>Drexel's Improved Master Schedule</title>
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
	<script src="schedule.js"></script>
</head>
<body>
	<select id="subject_select" onchange="subject_select_onchange();">
		<option>None</option>
		<?php
			echo passthru("./get_subjects.py");
		?>
	</select>
	<select id="number_select"></select>
	<button id="go_button" onclick="go();">Go</button>
	<br>
	<div id="quarters"></div>
</body>
</html>

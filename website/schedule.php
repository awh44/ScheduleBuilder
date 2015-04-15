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
			$db = new SQLite3('../data/courses.db');
			$results = $db->query('SELECT subj_id, name FROM subjects ORDER BY name');
			while ($row = $results->fetchArray())
			{
				echo '<option value="' . $row['subj_id'] . '">' . $row['name'] . '</option>';
			}
		?>
	</select>
	<select id="number_select"></select>
	<button id="go_button" onclick="go();">Go</button>
	<br>
	<div id="quarters"></div>
</body>
</html>

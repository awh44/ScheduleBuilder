<html>
<head>
	<title>Drexel's Improved Term Master Schedule</title>
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
	<script src="query.js"></script>
</head>
<body>
	Get courses where:
	<div id="filter-rows">
		<div class="filter-row">
			<select class="type">
				<option value="subject">Subject</option>
				<option value="number">Number</option>
				<option value="name">Name</option>
				<option value="credits">Credits</option>
				<option value="season">Season</option>
				<option value="year">Year</option>
				<option value="campus">Campus</option>
				<option value="capacity">Capacity</option>
				<option value="taken">Taken</option>
				<option value="instructor">Instructor</option>
				<option value="day-time">Day and Time</option>
				<option value="(">Left Parenthesis</option>
				<option value=")">Right Parenthesis</option>
			</select>
			<span class="operator">
				Equals
			</span>
			<select class="data">
				<?php
					echo passthru("./get_subjects.py");
				?>
			</select>
			<select class="negate">
				<option value="no">No</option>
				<option value="yes">Yes</option>
			</select>
			<select class="logical">
				<option value=""></option>
				<option value="and">And </option>
				<option value="or">Or</option>
			</select>
			<button class="delete" disabled="true">Delete</button>
		</div>
	</div>
</body>
</html>

<html>
<head>
	<title>Drexel's Improved Master Schedule</title>
	<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
	<script>
		function go()
		{
			$("#quarters").empty();
			var course_id = $("#number_select").val();
			$.ajax({
				"type": "POST",
				"data": { "course_id": course_id },
				"url": "get_quarters.php",
				"success": function (data)
					{
						var quarters = JSON.parse(data);
						for (var key in quarters)
						{
							var new_span = $("<span/>").text(quarters[key]);	
							$("#quarters").prepend(new_span).prepend("<br/>");
						}
					}
				});
		}

		$(document).ready(function ()
			{
				$("#subject_select").on("change", function ()
					{
						$("#number_select").empty();
						var subj_id = ($("#subject_select").val());
						$.ajax({
							"type": "POST",
							"data": { "subj_id": subj_id },
							"url": "get_numbers.php",
							"success": function (data)
								{
									var numbers = JSON.parse(data);
									console.log(numbers);
									for (var key in numbers)
									{
										var numberObj = numbers[key];
										var course_id = numberObj["course_id"];
										var course_number = numberObj["number"];
										var course_name = numberObj["name"];
										var new_option = $("<option/>").val(course_id).text(course_number + " " + course_name);
										$("#number_select").append(new_option);
									}
								}
							});
					});
			});
	</script>
</head>
<body>
	<?php
		$subject_select = '<select id="subject_select"><option>None</option>';
		$db = new SQLite3('../data/courses.db');
		$results = $db->query('SELECT subj_id, name FROM subjects ORDER BY name');
		while ($row = $results->fetchArray())
		{
			$subject_select .= '<option value="' . $row['subj_id'] . '">' . $row['name'] . '</option>';	
		}
		$subject_select .= '</select>';	
		echo $subject_select;

		echo ' ';
	
		$number_select = '<select id="number_select"></select>';
		echo $number_select;

		echo ' ';

		$go_button = '<button id="go_button" onclick="go();">Go</button>';
		echo $go_button;

		echo '<br>';

		echo '<div id="quarters"></div>';
	?>
</body>
</html>

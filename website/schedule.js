function go()
{
	$("#quarters").empty();
	var course_id = $("#number_select").val();
	$.ajax(
		{
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

function subject_select_onchange()
{
	$("#number_select").empty();
	var subj_id = $("#subject_select").val();
	if (subj_id !== "None")
	{
		$.ajax(
				{
					"type": "POST",
					"data": { "subj_id": subj_id },
					"url": "get_numbers.php",
					"success":
						function (data)
						{
							var numbers = JSON.parse(data);
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
					}
			   );
	}
}

$(document).ready(function ()
{
	$("#subject_select").val("None").change();
});

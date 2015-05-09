function append_row()
{
	$new_row = $(".filter-row").first().clone();
	$new_row.children(".logical").on("change", create_logical_onchange());
	$new_row.children(".delete").removeAttr("disabled").on("click", function (e)
	{
		if ($(this).parent().nextAll().size() === 0)
		{
			alert("setting val.");
			$(this).parent().prev().children(".logical").val("").change();
		}
		$(this).parent().remove()
	});
	$("#filter-rows").append($new_row);
}

function create_logical_onchange()
{
	var previous = "";
	return function (e)
	{
		alert("change handler called.");
		if (this.value === "")
		{
			$(this).parent().nextAll().remove();
		}
		else if (previous === "")
		{
			append_row();
		}
		previous = this.value;
	}
}

$(document).ready(function ()
{
	$(".logical").on("change", create_logical_onchange());
});

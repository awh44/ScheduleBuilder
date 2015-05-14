function append_row()
{
	$new_row = $(".filter-row").first().clone();
	$new_row.children(".type").on("change", type_onchange).val("number").change();
	$new_row.children(".logical").on("change", create_logical_onchange());
	$new_row.children(".delete").removeAttr("disabled").on("click", function (e)
	{
		var $parent = $(this).parent();
		if ($parent.nextAll().size() === 0)
		{
			$parent.prev().children(".logical").val("").change();
		}
		$parent.remove()
	});
	$("#filter-rows").append($new_row);
}

function create_input(type, css_class)
{
	return $("<input type=\"" + type + "\" class=\"" + css_class + "\"></input>");
}

function create_select(css_class)
{
	return $("<select class=\"" + css_class + "\"></select>");
}

function add_option($element, value, text)
{
	$element.append("<option value=\"" + value + "\">" + text + "</option>");
}

function create_math_operators()
{
	var $operators = create_select("operator");
	add_option($operators, "lt", "Less Than");
	add_option($operators, "le", "Less Than or Equal To");
	add_option($operators, "et", "Equal To");
	add_option($operators, "ge", "Greater Than or Equal To");
	add_option($operators, "gt", "Greater Than");

	return $operators;
}

function type_onchange(e)
{
	var $parent = $(this).parent();
	if (this.value === "subject")
	{
		$.ajax({ "type": "POST", "data": {}, "url": "get_subjects.php", "success": function (data)
		{
			$parent.children(".data").replaceWith("<select class=\"data\">" + data + "</select>");
			$parent.children(".operator").replaceWith("<span class=\"operator\">Equals</span>");
		}});
	}
	else if (this.value === "number" || this.value === "credits")
	{
		$parent.children(".data").replaceWith(create_input("number", "data"));
		$parent.children(".operator").replaceWith(create_math_operators());
	}
	else if (this.value === "name")
	{
		$parent.children(".data").replaceWith(create_input("text", "data"));
		var $select = create_select("operator");
		add_option($select, "equals", "Equals");
		add_option($select, "like", "Like");
		$parent.children(".operator").replaceWith($select);
	}
	
}

function create_logical_onchange()
{
	var previous = "";
	return function (e)
	{
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
	$(".type").on("change", type_onchange).change();
	$(".logical").on("change", create_logical_onchange());
});

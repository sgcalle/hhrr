var contador = -1;

function addSchool() {
	var schoolClonnable = document.getElementById("form-template").cloneNode(
			true);
	var schoolForms = document.getElementById("school_forms");

	schoolForms.appendChild(schoolClonnable)

	contador--;
	$(schoolClonnable).attr("id", "previous_school_" + contador)
	$(schoolClonnable).removeClass("d-none");
	var removeButton = $(schoolClonnable).find("button")
	$(removeButton).data("id", contador).on("click", removeSchool);

	$(this).remove();

	$("#school_forms").append("<button type='button' class='add-school btn btn-success d-block m-auto'>Add School</button>");
	$(".add-school").on("click", addSchool);
}

function changeState() {
	var select_state = $(this).parents("div.row").find("select.state")
	select_state.children("option:gt(0)").hide();
	select_state.children("option[data-country='" + $(this).val() + "']").show();

	if (select_state.children("option:selected").is(":hidden")){
		select_state.children("option:nth(0)").prop("selected", true);
	}
}

function removeSchool() {
	id = $(this).data("id");
	$("#previous_school_" + id).remove();
	$(this).remove();
}

$(document).ready(function() {
	$(".add-school").on("click", addSchool);
	$(".remove-school").on("click", removeSchool);
	$("select.country").on("change", changeState);
	$("select.country").trigger("change");
});
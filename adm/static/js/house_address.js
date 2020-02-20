var contador = -1;

function addHomeAddress() {
	var house_addressClonnable = document.getElementById("form-template").cloneNode(true);
	var house_addressForms = document.getElementById("house_address_forms");
	
	
	house_addressForms.appendChild(house_addressClonnable)

	contador--;
	$(house_addressClonnable).attr("id", "house_address_" + contador)
	$(house_addressClonnable).removeClass("d-none");
	var removeButton = $(house_addressClonnable).find("button")
	$(removeButton).data("id", contador).on("click", removeHomeAddress);

	$(this).remove();

	$("#house_address_forms").append("<button type='button' class='add-house_address btn btn-success d-block m-auto'>Add HomeAddress</button>");
	$(".add-house_address").on("click", addHomeAddress);
	$(house_addressForms).find("select.country").on("change", changeState);
}

function changeState() {
	var select_state = $(this).parents("div.row").find("select.state")
	select_state.children("option:gt(0)").hide();
	select_state.children("option[data-country='" + $(this).val() + "']").show();

	if (select_state.children("option:selected").is(":hidden")){
		select_state.children("option:nth(0)").prop("selected", true);
	}
}

function removeHomeAddress() {
	id = $(this).data("id");
	$("#house_address_" + id).remove();
	$(this).remove();
}

$(document).ready(function() {
	$(".add-house_address").on("click", addHomeAddress);
	$(".remove-house_address").on("click", removeHomeAddress);
	$("select.country").on("change", changeState);
	$("select.country").trigger("change");
});
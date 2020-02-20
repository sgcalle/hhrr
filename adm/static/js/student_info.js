function disableElementsInForm(event) {
	event.preventDefault();
//	$("[value='-1']").each(function() {
//		$(this).prop("disabled", true);
//	})
	document.getElementById("info-form").submit();
}

$(function() {
	document.getElementById("info-form").addEventListener("submit",
			disableElementsInForm);
});

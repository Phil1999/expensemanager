// This function is used in edit_expenses.html to create a confirmation window before deleting a
// transaction
const element = document.querySelector(".confirm-delete")

$(element).on('click', function () {
     return confirm("Do you want to delete this expense?");
});
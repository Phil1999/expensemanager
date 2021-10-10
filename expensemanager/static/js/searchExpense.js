const searchField = document.querySelector("#searchField")
const tableOutput = document.querySelector(".table-output")
const appTable = document.querySelector(".app-table")
const pagination = document.querySelector(".pagination-container")

const tbody = document.querySelector(".table-body")
const noResults = document.querySelector(".no-results");

tableOutput.style.display = "none";


searchField.addEventListener('keyup', (e) => {
    const search_str = e.target.value
    
    if (search_str.trim().length > 0) {
        pagination.style.display = "none"
        tbody.innerHTML = ""
        fetch('search-expense', {
            body: JSON.stringify({ searchText: search_str }), // We have to stringify our objects
            method: "POST",
        })
            .then((res) => res.json())
            .then((data) => {
                console.log("data", data)
                appTable.style.display = "none"
                tableOutput.style.display = "block"

                if (data.length === 0) {
                    noResults.style.display = "block";
                    tableOutput.style.display = "none"
                    
                } else {
                    noResults.style.display = "none";
                    data.forEach((item) => {
                    // Need to use backticks when referencing dynamic data
                        tbody.innerHTML += `
                        <tr>
                            <td> ${item.amount_spent} </td>
                            <td> ${item.category} </td>
                            <td> ${item.description} </td>
                            <td> ${item.date} </td>
                        </tr>`
                    })
                }
        });
    }else {
        noResults.style.display = "none";
        appTable.style.display = "block"
        pagination.style.display = "block"
        tableOutput.style.display = "none"
    }

});
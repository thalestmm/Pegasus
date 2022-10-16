var renderedRowsCounter = 1;

function append_row(row_n) {
    let tbodyRef = document.getElementById('RouteTable').getElementsByTagName('tbody')[0];
    let newRow = tbodyRef.insertRow();

    let index = renderedRowsCounter + 1;
    newRow.insertCell(0).outerHTML = "<th>" + index + "</th>";  // rather than innerHTML

    // Inserts new cells at the end of the row
    let Departure    = newRow.insertCell();
    let Arrival      = newRow.insertCell();
    let Alternative  = newRow.insertCell();

    // Get last Arrival to set new Departure
    let lastArrival  = document.getElementById(`arr_${renderedRowsCounter-1}`).value;

    // Append a text node to the cell
    let depField = document.createElement("INPUT");
    depField.setAttribute("type", "text");
    depField.setAttribute("maxLength", 4);
    depField.setAttribute("name", `dep_${renderedRowsCounter}`);
    depField.setAttribute("value", lastArrival);
    depField.classList.add("form-control");
    depField.id = `dep_${renderedRowsCounter}`;
    depField.setAttribute("oninput","this.value = this.value.toUpperCase()");

    Departure.appendChild(depField);

    let arrField = document.createElement("INPUT");
    arrField.setAttribute("type", "text");
    arrField.setAttribute("maxLength", 4);
    arrField.setAttribute("name", `arr_${renderedRowsCounter}`);
    arrField.classList.add("form-control");
    arrField.id = `arr_${renderedRowsCounter}`;
    arrField.setAttribute("oninput","this.value = this.value.toUpperCase()");


    Arrival.appendChild(arrField);

    let altField = document.createElement("INPUT");
    altField.setAttribute("type", "text");
    altField.setAttribute("maxLength", 4);
    altField.setAttribute("name", `alt_${renderedRowsCounter}`);
    altField.classList.add("form-control");
    altField.id = `alt_${renderedRowsCounter}`;
    altField.setAttribute("oninput","this.value = this.value.toUpperCase()");


    Alternative.appendChild(altField);

}

var buttonClick = document.getElementById("addRow");

buttonClick.addEventListener('click', event => {
  append_row(row_n=renderedRowsCounter);
  renderedRowsCounter += 1;
});
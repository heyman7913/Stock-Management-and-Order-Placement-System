/*
var c = 1;
var row, productID, productName, priceUnit, quantity, subTotal, grandTotal;

// Flag to track if the first item is added
var isFirstItemAdded = false;

function addItem() {
    var table = document.getElementById("billingTable");
    if (document.getElementById("productID").value <= 0 || document.getElementById("productID").value == null || document.getElementById("productID").value == "") {
        alert("This value is an invalid product ID and cannot be entered into the table. Please try again.");
        document.getElementById("productID").value = "";
        return;
    }
    let checkRepeatItem = checkInCart(document.getElementById("productID").value);
    if (checkRepeatItem[0] == true) {
        alert("You have entered the same item again. Please go to table and edit the quantity at Row Number " + checkRepeatItem[1])
        return;
    }
    var row = table.insertRow(-1);
    var productID = row.insertCell(0);
    var productName = row.insertCell(1);
    var priceUnit = row.insertCell(2);
    var quantity = row.insertCell(3);
    var subTotal = row.insertCell(4);
    productID.innerHTML = document.getElementById("productID").value;
    quantity.innerHTML = 1 + "<button class=\"plusBtn\" onclick = \"plusItem(this)\"><i class=\"fa fa-plus\"></i></button><button onclick = \"minusItem(this)\" class=\"minusBtn\" style=\"font-size:24px\"><i class=\"fa fa-minus\"></i></button>";
    document.getElementById("productID").value = "";

    // Show popup only once when the first item is added
    if (!isFirstItemAdded) {
        showPopup();
        isFirstItemAdded = true;
    }
}

function checkInCart(checkItem) {
    var repeatRow = 0;
    var itemFound = false;
    var table = document.getElementById("billingTable");
    for (let i = 1; i < table.rows.length; i++) {
        if (checkItem == table.rows[i].cells[0].innerHTML) {
            console.log("Same item detected");
            repeatRow = i;
            itemFound = true;
        }
    }
    if (itemFound == true) {
        return [true, repeatRow];
    } else {
        return [false, 0];
    }
}

function plusItem(element) {
    var table = document.getElementById("billingTable");
    table.rows[element.parentNode.parentNode.rowIndex].cells[3].innerHTML = parseInt(table.rows[element.parentNode.parentNode.rowIndex].cells[3].innerHTML) + 1 + "<button class=\"plusBtn\" onclick = \"plusItem(this)\"><i class=\"fa fa-plus\"></i></button><button onclick = \"minusItem(this)\" class=\"minusBtn\" style=\"font-size:24px\"><i class=\"fa fa-minus\"></i></button>";
}

function minusItem(element) {
    var table = document.getElementById("billingTable");
    if (parseInt(table.rows[element.parentNode.parentNode.rowIndex].cells[3].innerHTML) == 1) {
        var remove = confirm("Reducing the quantity further will remove the item from the cart. Please confirm if you want to do so")
        if (remove == true) {
            document.getElementById("billingTable").deleteRow(element.parentNode.parentNode.rowIndex);
            c = document.getElementById("billingTable").rows.length;
            console.log(c + " delete");
        }
    } else {
        table.rows[element.parentNode.parentNode.rowIndex].cells[3].innerHTML = parseInt(table.rows[element.parentNode.parentNode.rowIndex].cells[3].innerHTML) - 1 + "<button class=\"plusBtn\" onclick = \"plusItem(this)\"><i class=\"fa fa-plus\"></i></button><button onclick = \"minusItem(this)\" class=\"minusBtn\" style=\"font-size:24px\"><i class=\"fa fa-minus\"></i></button>";
    }
}
*/

function confirmDelete() {
    return confirm("Are you sure you want to delete this item from the cart?");
}

function confirmClear() {
    return confirm("Are you sure you want to clear the cart?");
}

document.addEventListener("DOMContentLoaded", function() {
    // Check if the billing table has more than 1 row before showing the popup
    var table = document.getElementById("billingTable");
    if (table.rows.length <= 1) {
        createPopup();
    }
});

function createPopup() {
    // Create the overlay
    var overlay = document.createElement("div");
    overlay.id = "overlay";
    overlay.className = "overlay";
    document.body.appendChild(overlay);

    // Create the popup element
    var popup = document.createElement("div");
    popup.id = "warningPopup";
    popup.className = "popup";

    // Create the popup content
    var popupContent = document.createElement("div");
    popupContent.className = "popup-content";

    var popupHeader = document.createElement("div");
    popupHeader.className = "popup-header";
    popupHeader.innerText = "Warning!";
    popupContent.appendChild(popupHeader);

    var paragraph = document.createElement("p");
    paragraph.className = "popup-message"; // Added class for styling
    paragraph.innerText = "Before sale, please check if the Customer has the prescription.";
    popupContent.appendChild(paragraph);

    var closeButton = document.createElement("button");
    closeButton.className = "popup-close close-btn";
    closeButton.innerText = "Close";
    closeButton.onclick = closePopup;
    popupContent.appendChild(closeButton);

    popup.appendChild(popupContent);

    // Append the popup to the body
    document.body.appendChild(popup);

    // Disable scrolling on the body
    document.body.style.overflow = "hidden";
}

function closePopup() {
    // Hide the popup
    var popup = document.getElementById("warningPopup");
    popup.style.display = "none";

    // Hide the overlay
    var overlay = document.getElementById("overlay");
    overlay.style.display = "none";

    // Enable scrolling on the body
    document.body.style.overflow = "auto";
}

var c=1;
			var row, productID, productName, price, qtyAvailable, shelfLocation, acceptReturns, reorderQty, otherQtyAvailable, otherReorderQuantity, deleteBtn;

            function addItem(){
				var table = document.getElementById("inventoryTable");
                console.log(c);
                if(document.getElementById("productName").value == null || document.getElementById("productName").value == "" || document.getElementById("productPrice").value < 0 ||  document.getElementById("productPrice").value == null || document.getElementById("shelfLocation").value == null || document.getElementById("shelfLocation").value == "" || document.getElementById("acceptReturns").value == "Accept Returns" || document.getElementById("quantityAvailable").value == "Quantity Available" || document.getElementById("reorderQty").value == "Reorder Quantity"){
                    alert("All values have not been filled out in the text box below. Item cannot be added. Please try again.");
                    return;
                }
                var row = table.insertRow(-1);
                var productID = row.insertCell(0);
  				var productName = row.insertCell(1);
  				var price= row.insertCell(2);
                var qtyAvailable= row.insertCell(3);
                var shelfLocation= row.insertCell(4);
                var acceptReturns= row.insertCell(5);
                var reorderQty= row.insertCell(6);
                var editItemInfo = row.insertCell(7);
                var deleteBtn = row.insertCell(8);
                editItemInfo.innerHTML = "<button class=\"editItemInfo\" onclick = \"window.location.href = '/employee/editItemInfo'\"\"style=\"font-size:24px;\"><i class = \"fa fa-edit center\"></i></button>";
                deleteBtn.innerHTML = "<button class=\"deleteButton\" onclick =\"deleteItem(this)\"><i class=\"ri-delete-bin-line\"></i></button>";

                if(document.getElementById("quantityAvailable").value == "Other"){
                    otherQtyAvailable = prompt("Please enter the quantity available for " + document.getElementById("productName").value);
                    while(otherQtyAvailable < 0){
                        alert("This is not valid input for this field");
                        otherQtyAvailable = prompt("Please enter the quantity available for " + document.getElementById("productName").value);
                    }
                    if (otherQtyAvailable>0){
                        qtyAvailable.innerHTML = otherQtyAvailable; //+  "<button class=\"editItemInfo\" \"style=\"font-size:24px;\" onclick = \"editItemInfo(this)\"><i class = \"fa fa-edit center\"></i></button>";
                    }
                }else{
                    qtyAvailable.innerHTML = document.getElementById("quantityAvailable").value;//+ "<button class=\"editItemInfo\" \"style=\"font-size:24px;\" onclick = \"editItemInfo(this)\"><i class = \"fa fa-edit center\"></i></button>";
                }

                if(document.getElementById("reorderQty").value == "Other"){
                    otherReorderQuantity = prompt("Please enter the reorder quantity for " + document.getElementById("productName").value);
                    while(otherReorderQuantity < 0){
                        alert("This is not valid input for this field");
                        otherReorderQuantity = prompt("Please enter the reorder quantity for " + document.getElementById("productName").value);
                    }
                    if (reorderQty>0){
                        reorderQty.innerHTML = otherQtyAvailable;// +  "<button class=\"editItemInfo\" \"style=\"font-size:24px;\" onclick = \"editItemInfo(this)\"><i class = \"fa fa-edit center\"></i></button>";
                    }
                }else{
                    reorderQty.innerHTML = document.getElementById("reorderQty").value ;//+  "<button class=\"editItemInfo\" \"style=\"font-size:24px;\" onclick = \"editItemInfo(this)\"><i class = \"fa fa-edit center\"></i></button>";
                }
				productID.innerHTML = c++;
  				productName.innerHTML = document.getElementById("productName").value ;
                price.innerHTML = document.getElementById("productPrice").value;// +  "<button class=\"editItemInfo\" \"style=\"font-size:24px;\" onclick = \"editItemInfo(this)\"><i class = \"fa fa-edit center\"></i></button>";
				shelfLocation.innerHTML = document.getElementById("shelfLocation").value;// +  "<button class=\"editItemInfo\" \"style=\"font-size:24px;\" onclick = \"editItemInfo(this)\"><i class = \"fa fa-edit center\"></i></button>";
                acceptReturns.innerHTML = document.getElementById("acceptReturns").value ;
                document.getElementById("productName").value = "";
                document.getElementById("productPrice").value = "";
                document.getElementById("shelfLocation").value = "";
                document.getElementById("acceptReturns").value = "Accept Returns";
                document.getElementById("reorderQty").value = "Reorder Quantity";
                document.getElementById("quantityAvailable").value = "Quantity Available";
			};
            function deleteItem(element){
                var table = document.getElementById("inventoryTable");
                var remove = confirm("This action will delete the item from the inventory and delete all pertaining records in other tables. Please confirm if you would like to do so.")
                if (remove == true){
						document.getElementById("inventoryTable").deleteRow(element.parentNode.parentNode.rowIndex);
						c = document.getElementById("inventoryTable").rows.length;
						console.log(c + " delete");
						for(let i=1; i<=document.getElementById("inventoryTable").rows.length; i++){ // changing the serial numbers after the delete happens
							table.rows[i].cells[0].innerHTML = i;
					}
				}
            }
            /*function editItemInfo(element){	// Function for the edit icon which appears next to the item name in the table. It allows a user to correct any mistakes in the names of products.
				var table = document.getElementById("inventoryTable");
				var newValue = prompt("Please enter the new value for this field"); //FOr the Accept Returns column - separate function
				if (newValue == table.rows[element.parentNode.parentNode.rowIndex].cells[element.parentNode.cellIndex].innerHTML){
					alert("The same value has been entered again");
				}else if (newValue == null || newValue == "") {
					alert("Null isn't an appropriate value for this field. If you would like to change the value for this cell, please click the edit icon again. ");
				}else{
					table.rows[element.parentNode.parentNode.rowIndex].cells[element.parentNode.cellIndex].innerHTML = newValue + "<button class=\"editItemInfo\" \"style=\"font-size:24px;\" onclick = \"editItemInfo(this)\"><i class = \"fa fa-edit center\"></i></button>";
				}

			};*/

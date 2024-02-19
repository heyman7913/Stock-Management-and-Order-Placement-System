/*
var c = 1;
            var row, productID, productName, priceUnit, quantityRet, acceptReturns;
            function returnItem(){
                var table = document.getElementById("returnTable");
                if (document.getElementById("productID").value <= 0 || document.getElementById("productID").value == null || document.getElementById("productID").value == "" ){
                    alert("This value is an invalid product ID and cannot be entered into the table. Please try again.");
                    document.getElementById("productID").value = "";
                    return;
                }
                let checkRepeatItem = checkInCart(document.getElementById("productID").value);
                if (checkRepeatItem[0] == true){
                    alert("You have entered the same item again. Please go to table and edit the quantity at Row Number " + checkRepeatItem[1])
                    return;
                }
                var row = table.insertRow(-1);
                var productID = row.insertCell(0);
  			    var productName = row.insertCell(1);
  			    var priceUnit = row.insertCell(2);
                var quantityRet= row.insertCell(3);
                var acceptReturns= row.insertCell(4);
                productID.innerHTML = document.getElementById("productID").value;
                quantityRet.innerHTML = 1 + "<button class=\"plusBtn\" onclick = \"plusItem(this)\"><i class=\"fa fa-plus\"></i></button><button onclick = \"minusItem(this)\" class=\"minusBtn\" style=\"font-size:24px\"><i class=\"fa fa-minus\"></i></button>";
                document.getElementById("productID").value = ""
            }
            function checkInCart(checkItem){
                var repeatRow = 0;
                var itemFound = false;
                var table = document.getElementById("returnTable");
                for (let i = 1; i < table.rows.length; i ++){
                    if (checkItem == table.rows[i].cells[0].innerHTML){
                        console.log("Same item detetced");
                        repeatRow = i;
                        itemFound = true;
                    }
                }
                if (itemFound == true){
                    return [true, repeatRow];
                }
                else{
                    return [false, 0];
                }
            }
            function plusItem(element){
                var table = document.getElementById("returnTable");
				table.rows[element.parentNode.parentNode.rowIndex].cells[3].innerHTML = parseInt(table.rows[element.parentNode.parentNode.rowIndex].cells[3].innerHTML) + 1 +"<button class=\"plusBtn\" onclick = \"plusItem(this)\"><i class=\"fa fa-plus\"></i></button><button onclick = \"minusItem(this)\" class=\"minusBtn\" style=\"font-size:24px\"><i class=\"fa fa-minus\"></i></button>";
            }
            function minusItem(element){
                var table = document.getElementById("returnTable");
				if (parseInt(table.rows[element.parentNode.parentNode.rowIndex].cells[3].innerHTML) == 1){
					var remove = confirm("Reducing the quantity further will remove the item from the return cart. Please confirm if you want to do so")
					if (remove == true){
						document.getElementById("returnTable").deleteRow(element.parentNode.parentNode.rowIndex);
						c = document.getElementById("returnTable").rows.length;
						console.log(c + " delete");
					}
				}else{
					table.rows[element.parentNode.parentNode.rowIndex].cells[3].innerHTML = parseInt(table.rows[element.parentNode.parentNode.rowIndex].cells[3].innerHTML) - 1 + "<button class=\"plusBtn\" onclick = \"plusItem(this)\"><i class=\"fa fa-plus\"></i></button><button onclick = \"minusItem(this)\" class=\"minusBtn\" style=\"font-size:24px\"><i class=\"fa fa-minus\"></i></button>";
				}
            }*/

function confirmDeleteItem() {
    return confirm("Are you sure you want to delete this item from the return order?\nThis action cannot be undone.");
}


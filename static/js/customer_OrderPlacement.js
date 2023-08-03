var c=1;
			var row, serial_no, item, qty, otherQty;

			function addItem(){   // Function to transfer item from the text box for user input into the table.
				var table = document.getElementById("orders_table");
				if(document.getElementById("itemName_input").value == "" || document.getElementById("itemName_input").value == null){
					alert("Item cannot be inserted into table as there is no name. Please try again after writing the name in the text box below.");
					return;
				}
  				var row = table.insertRow(-1);
  				var serial_no = row.insertCell(0);
				console.log(c);
  				var item = row.insertCell(1);
  				var qty = row.insertCell(2);
				var editQtyBtn = row.insertCell(3);
				editQtyBtn.innerHTML = "<button class=\"plusBtn\" onclick = \"plusItem(this)\" style=\"font-size:10px\"><i class=\"fa fa-plus\"></i></button><button onclick = \"minusItem(this)\" class=\"minusBtn\" style=\"font-size:10px\"><i class=\"fa fa-minus\"></i></button>";
				serial_no.innerHTML = c++;
  				item.innerHTML = document.getElementById("itemName_input").value ;
				if (document.getElementById("quantity_input").value == "Other"){
					otherQty = prompt("Please enter the quantity of " + document.getElementById("itemName_input").value + " you wish to buy");
					if (otherQty > 0){
						qty.innerHTML = otherQty;
					}else{
						alert("Sorry this item cannot be added to the list as quantity mentioned is negative");
						return;
					}
				}else{
					qty.innerHTML = document.getElementById("quantity_input").value;
				}
				document.getElementById("itemName_input").value="";
				document.getElementById("quantity_input").value="1";
			};


			function plusItem(element){  // Increase quantity of the item at a later stage.
				var table = document.getElementById("orders_table");
				table.rows[element.parentNode.parentNode.rowIndex].cells[2].innerHTML = parseInt(table.rows[element.parentNode.parentNode.rowIndex].cells[2].innerHTML) + 1;
			}
			function minusItem(element){  // Reduce quantity and delete the product from the table.
				var table = document.getElementById("orders_table");
				if (parseInt(table.rows[element.parentNode.parentNode.rowIndex].cells[2].innerHTML) == 1){
					var remove = confirm("Reducing the quantity further will remove the item from the cart. Please confirm if you want to do so")
					if (remove == true){
						document.getElementById("orders_table").deleteRow(element.parentNode.parentNode.rowIndex);
						c = document.getElementById("orders_table").rows.length;
						console.log(c + " delete");
						for(let i=1; i<=document.getElementById("orders_table").rows.length; i++){ // changing the serial numbers after the delete happens
							table.rows[i].cells[0].innerHTML = i;
					}
					}
				}else{
					table.rows[element.parentNode.parentNode.rowIndex].cells[2].innerHTML = parseInt(table.rows[element.parentNode.parentNode.rowIndex].cells[2].innerHTML) - 1;
				}

			}
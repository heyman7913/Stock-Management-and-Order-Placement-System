var c=1;
			var row, userID, firstName, lastName, emailID, password, deleteBtn, pwdDB;
            function addUser(){
				var table = document.getElementById("userTable");
                console.log(c);
                if(document.getElementById("EmpFirstName").value == null || document.getElementById("EmpFirstName").value == "" || document.getElementById("EmpLastName").value == null || document.getElementById("EmpLastName").value == "" || document.getElementById("EmpEmailID").value == null || document.getElementById("EmpEmailID").value == "" || document.getElementById("EmpPassword").value == null || document.getElementById("EmpPassword").value == "") {
                    alert("All values have not been filled out in the text box below. User access cannot be granted. Please try again.");
                    return;
                }
                var row = table.insertRow(-1);
                var userID = row.insertCell(0);
                var firstName = row.insertCell(1);
  				var lastName = row.insertCell(2);
  				var emailID= row.insertCell(3);
                var password= row.insertCell(4);
                var deleteBtn = row.insertCell(5);
                deleteBtn.innerHTML = "<button class=\"deleteButton\" onclick =\"deleteUser(this)\"><i class=\"ri-delete-bin-line\"></i></button>"
                password.innerHTML = "<button class=\"editUserPassword\" \"style=\"font-size:24px;\" onclick = \"editUserPassword(this)\"><i class = \"fa fa-edit center\"></i></button>"

				userID.innerHTML = c++;
  				firstName.innerHTML = document.getElementById("EmpFirstName").value ;
                lastName.innerHTML = document.getElementById("EmpLastName").value ;
				emailID.innerHTML = document.getElementById("EmpEmailID").value ;

			    // This variable will be used to transfer the password into the database
                pwdDB = document.getElementById("EmpPassword").value ;
                // console.log(pwdDB);

                document.getElementById("EmpFirstName").value = "";
                document.getElementById("EmpLastName").value = "";
                document.getElementById("EmpEmailID").value = "";
                document.getElementById("EmpPassword").value = "";
			};
            function deleteUser(element){
                var table = document.getElementById("userTable");
                var remove = confirm("This action will delete the user's access!!! \nPlease confirm if you would like to do so.")
                if (remove == true){
						document.getElementById("userTable").deleteRow(element.parentNode.parentNode.rowIndex);
						c = document.getElementById("userTable").rows.length;
						// console.log(c + " delete");
						for(let i=1; i<=document.getElementById("userTable").rows.length; i++){ // changing the serial numbers after the delete happens
							table.rows[i].cells[0].innerHTML = i;
					}
				}
            }
            function editUserPassword(element){	// Function for the edit icon which appears in the change password column. It will allow the admin to change the password if a user forgets it.
				var table = document.getElementById("userTable");
				editPWD = confirm("This action will edit the current password for the user " + table.rows[element.parentNode.parentNode.rowIndex].cells[1].innerHTML + ".\nPlease click 'Ok' if you would like to continue.")
				if(editPWD == true){
				    var newPasswordDB = prompt("Please enter the new password for the user " + table.rows[element.parentNode.parentNode.rowIndex].cells[1].innerHTML); //Accepts the new password
				    while (newPasswordDB == null || newPasswordDB == ""){
				        newPasswordDB = prompt("The password you entered was invalid. \nPlease try again.")
				    }
				    alert("Password successfully updated")
				}
				else{
				    alert("Process ABORTED")
				}
			};
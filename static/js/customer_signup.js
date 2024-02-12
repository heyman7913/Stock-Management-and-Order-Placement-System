
function checkMatching(){
                console.log("function called")
                var textbox1Value = document.getElementById("psw").value;
                var textbox2Value = document.getElementById("psw-repeat").value;
                var submitBtn = document.getElementById("submitBtn");
                if (textbox1Value != textbox2Value) {
                    alert ("\nPassword did not match: Please try again...")
                    submitBtn.disabled = true;
                }
                else{
                    submitBtn.disabled = false;
                }

}
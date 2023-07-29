function checkMatching() {
            var textbox1Value = document.getElementById("psw").value;
            var textbox2Value = document.getElementById("psw-repeat").value;
            var submitBtn = document.getElementById("submitBtn");

            if (textbox1Value === textbox2Value) {
                submitBtn.disabled = false;
            } else {
                submitBtn.disabled = true;
            }
        }
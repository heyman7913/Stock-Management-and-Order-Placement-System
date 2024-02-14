function populateYearDropdown() {
        var yearDropdown = document.getElementById("yearDropdown");

        var currentYear = new Date().getFullYear();

        var startYear = 2023;
        var endYear = currentYear + 100; // Display 10 years after the current year


        for (var year = startYear; year <= endYear; year++) {
            var option = document.createElement("option");
            option.text = year;
            yearDropdown.add(option);
        }
    }

function openPopup(period, totalOrders, monthlyRevenue) {
    var tableContent = `
        <div class="popup">
            <h2>Monthly Revenue Details - ${period}</h2>
            <table>
                <thead>
                    <tr>
                        <th>Total Number of Orders</th>
                        <th>Monthly Revenue</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>${totalOrders}</td>
                        <td>${monthlyRevenue}</td>
                    </tr>
                </tbody>
            </table>
            <button class="close-btn" onclick="closePopup()">Close</button>
            <button class="save-btn" onclick="savePopupAsImage()">Download</button>
            <a href="mailto:?subject=Monthly Revenue Report - ${period}&body=Total Orders: ${totalOrders}%0D%0A Monthly Revenue: ${monthlyRevenue}" target="_blank">Share via Email</a>
        </div>
        <div class="overlay" onclick="closePopup()"></div>
    `;
    document.body.insertAdjacentHTML('beforeend', tableContent);
}


function savePopupAsImage() {
    var popup = document.querySelector('.popup');
     var selectedMonth = document.getElementById("filterMonth").value;
    console.log(selectedMonth);
    var selectedYear = document.getElementById("yearDropdown").value;
    console.log(selectedYear);

    html2canvas(popup, {
        onrendered: function(canvas) {
            var link = document.createElement('a');
            link.download = 'monthly_revenue_details_'+ selectedMonth + '_' + selectedYear + '.png';
            link.href = canvas.toDataURL();
            link.click();
        }
    });
}

        function closePopup() {
            var popup = document.querySelector('.popup');
            var overlay = document.querySelector('.overlay');

            if (popup && overlay) {
                popup.remove();
                overlay.remove();
            }
        }

        function currentMonthRevenue() {
    // Get selected month and year
    var selectedMonth = document.getElementById("filterMonth").value;
    console.log(selectedMonth);
    var selectedYear = document.getElementById("yearDropdown").value;
    console.log(selectedYear);

    // Get the table element
    var table = document.getElementById("monthlyRevenueTable");

    // Get all rows from the table
    var rows = table.getElementsByTagName("tr");

    // Loop through all rows except the header row (index 0)
    for (var i = 1; i < rows.length; i++) {
        var row = rows[i];
        var cells = row.getElementsByTagName("td");

        // Check if the month and year match the selected values
        if (cells.length >= 3 && cells[0].innerText === selectedMonth + "/" + selectedYear) {
            // If match found, update the popup content with this row's data
            var totalOrders = cells[1].innerText;
            var monthlyRevenue = cells[2].innerText;

            // Open popup with the selected month and year's data
            openPopup(selectedMonth + "/" + selectedYear, totalOrders, monthlyRevenue);
            return; // Exit the function after finding the match
        }
    }

    // If no matching data found, display a message or handle it accordingly
    alert("No data found for the selected month and year.");
}


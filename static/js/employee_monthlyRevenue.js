function populateYearDropdown() {
        // Get the dropdown element
        var yearDropdown = document.getElementById("yearDropdown");

         // Get the current year
        var currentYear = new Date().getFullYear();

        // Define the range of years to display
        var startYear = currentYear; // Display 10 years before the current year
        var endYear = currentYear + 100; // Display 10 years after the current year

        // Populate the dropdown with options from the startYear to endYear
        for (var year = startYear; year <= endYear; year++) {
            var option = document.createElement("option");
            option.text = year;
            yearDropdown.add(option);
        }
    }
        function openPopup() {
            // Create the table content
            var tableContent = `
                <div class="popup">
                    <h2>Monthly Revenue Details</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Month/Year</th>
                                <th>Total Number of Orders</th>
                                <th>Monthly Revenue</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>January 2024</td>
                                <td>100</td>
                                <td>$5000</td>
                            </tr>
                            <!-- Add more rows here if needed -->
                        </tbody>
                    </table>
                    <button class="close-btn" onclick="closePopup()">Close</button>
                </div>
                <div class="overlay" onclick="closePopup()"></div>
            `;

            // Add the table content to the body
            document.body.insertAdjacentHTML('beforeend', tableContent);
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
            // Call this function when the "Filter Data" button is clicked
            openPopup();
        }

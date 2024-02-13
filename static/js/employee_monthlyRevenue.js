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

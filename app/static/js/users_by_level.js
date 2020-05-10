
        var values = [];
        var colors = [];
        var levels = [];
        {% for item in users_by_level %}
            levels.push({{item[0]}});
            values.push({{item[1]}});
            colors.push("{{item[2]}}");
        {% endfor %}
        


        // get bar chart canvas
        var mychart = document.getElementById("users_by_level").getContext("2d");
        var config = {
            type: 'pie',
            data: {
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                }],
                labels: levels
            },
            options: {
                responsive: true,
            }
        };
  
        // draw pie chart
        new Chart(document.getElementById("users_by_level").getContext("2d"), config);
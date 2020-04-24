var a = 0
var b = 1
var i;

a_field = document.getElementById('a')
a_field.addEventListener("change", updateChart)

b_field = document.getElementById('b')
b_field.addEventListener("change", updateChart)

var ctx = document.getElementById('chart').getContext('2d');
var chart

$(document).ready(function() {
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            datasets: [{
                label: "XP Needed for each level",
                borderColor: '#fcca03',
                data: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            }]
        },
        options: {
            legend: {
                display: true
            },

        }
    });
});


function xp(lvl) {
    return a*lvl*lvl + b*lvl
}


function updateChart() {
    chart.data.datasets[0].data = [];
    a = a_field.value
    b = b_field.value
    
    for (i = 1; i <= 10; i++) {
        chart.data.datasets[0].data.push(xp(i))
    }
    
    chart.update();
}

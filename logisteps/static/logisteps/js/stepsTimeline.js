function setWeekFilterText(start, end){
    const text = `${start.getMonth()+1}/${start.getDate()}/${start.getFullYear()} - ${end.getMonth()+1}/${end.getDate()}/${end.getFullYear()}`;
    document.getElementById("week_filter_text").innerText = text;
}

var lineChart = (function() {
    var end = new Date(2018,6,15);
    const start = new Date(end.valueOf());
    var chart;

    function changeDate(days) {
        end.setDate(end.getDate() + days);
        start.setDate(start.getDate() + days);
    }

    function formatData(data) {
        let xAxis = ['x'], countData = ['steps'];

        Object.keys(data).map((key, index) => {
            xAxis.push(key);
            countData.push(data[key]);
        });
        
        return {
            x: xAxis,
            data: countData
        }
    }

    function getData(start, end){
        const endPoint = '/api/steps/count/?';
        const url = `${endPoint}start=${start.getMonth()+1}-${start.getDate()}-${start.getFullYear()};end=${end.getMonth()+1}-${end.getDate()}-${end.getFullYear()}`

        return makeRequest('GET', url).then(result => {
            let data = JSON.parse(result);
            
            return formatData(data.count);
        });
    }

    function createChart(id, data) {
        return c3.generate({
            bindto: id,
            size: {
                height: 500
            },
            data: {
                x: 'x',
                columns: [
                    data.x,
                    data.data
                ],
                colors: {
                    steps: '#4A2B4B'
                }
            },
            axis: {
                x: {
                    type: 'category',
                }
            },
            legend: {
                hide: true
            }
        });
    }

    function refresh() {
        getData(start, end).then(data => {
            chart.load({
                columns: [
                    data.x,
                    data.data
                ]
            });
        });
        setWeekFilterText(start, end)
    }

    start.setDate(end.getDate() - 6);
    setWeekFilterText(start, end)
    getData(start, end).then(data => {
        chart = createChart('#linechart-week', data);
    })

    return {
        incrementDate: function () {
            changeDate(1);
            refresh();
        },
        decrementDate: function () {
            changeDate(-1);
            refresh();
        }
    }
})();

//TODO: add validation for increment and decrement
function decrementDay() {
    lineChart.decrementDate();
}

function incrementDay() {
    lineChart.incrementDate();
}

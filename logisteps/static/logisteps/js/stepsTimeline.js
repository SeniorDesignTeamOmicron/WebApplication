function setWeekFilterText(start, end){
    const text = `${start.getMonth()+1}/${start.getDate()}/${start.getFullYear()} - ${end.getMonth()+1}/${end.getDate()}/${end.getFullYear()}`;
    // document.getElementById("week_filter_text").innerText = text;
}

var lineChart = (function() {
    var end = new Date();
    let start = new Date(end.valueOf());
    let range = 6;
    var chart;

    function adjustRange(days) {
        if (days >= 6) {
            range = days;
            start = new Date(end)
            start.setDate(end.getDate() - days);
            refresh();
        }
    }

    function changeDate(days) {
        const today = new Date();

        if (validateDelta(days)) {
            end.setDate(end.getDate() + days);
            start.setDate(start.getDate() + days);
        }

        // Enable and disable buttons if needed
        if (days > 0) {
            if(!validateDelta(7)) {
                document.getElementById("increment_week").disabled = true;
            }

            if(end.getDate() == today.getDate()) {
                document.getElementById("increment_day").disabled = true;
            }
        }

        if (days < 0) {
            if(validateDelta(7)) {
                document.getElementById("increment_week").disabled = false;
            }

            if(end.getDate() < today.getDate()) {
                document.getElementById("increment_day").disabled = false;
            }
        }
    }

    function validateDelta(deltaDays) {
        const today = new Date();

        if (deltaDays <= 0) {
            return true;
        } else if (deltaDays > 0) {
            const temp = new Date(end);
            temp.setDate(end.getDate() + deltaDays);

            return temp.getDate() <= today.getDate();
        }
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

        document.getElementById('activity_loader').style.visibility="visible";
        return makeRequest('GET', url).then(result => {
            let data = JSON.parse(result);
            
            document.getElementById('activity_loader').style.visibility="hidden";
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
                    tick: {
                        rotate: 90,
                        multiline: false,
                        culling: {
                            max: 30
                        }
                    },
                    height: 90
                }
            },
            legend: {
                hide: true
            }
        });
    }

    function refresh() {
        getData(start, end).then(data => {
            chart.internal.xAxis.tickCulling(30);
            chart.load({
                columns: [
                    data.x,
                    data.data
                ]
            });
        });
        setWeekFilterText(start, end)
    }

    function init() {
        start.setDate(end.getDate() - 6);
        setWeekFilterText(start, end)
        document.getElementById("increment_day").disabled = true;
        document.getElementById("increment_week").disabled = true;
    }

    init();

    getData(start, end).then(data => {
        chart = createChart('#linechart-week', data);
    });

    return {
        incrementDate: function () {
            changeDate(1);
            refresh();
        },
        decrementDate: function () {
            changeDate(-1);
            refresh();
        },
        incrementWeek: function() {
            changeDate(7);
            refresh();
        },
        decrementWeek: function() {
            changeDate(-7);
            refresh();
        },
        adjustRange
    }
})();

//TODO: add validation for increment and decrement
function decrementDay() {
    lineChart.decrementDate();
}

function incrementDay() {
    lineChart.incrementDate();
}

function decrementWeek() {
    lineChart.decrementWeek();
}

function incrementWeek() {
    lineChart.incrementWeek();
}

function setRange(selectedOption) {
    const selectedRange = selectedOption.value;

    if(selectedRange === 'Week') {
        lineChart.adjustRange(6);
    } else if (selectedRange === 'Month') {
        lineChart.adjustRange(29);
    } else if(selectedRange === 'Year') {
        lineChart.adjustRange(364);
    }
}
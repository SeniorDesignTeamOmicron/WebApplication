var breakdownChart = (function() {
    function formatData(data) {
        const xAxis = ['x', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        let countData = ['steps'], activeTime = ['active'], inactiveTime = ['inactive'];

        //sort list by weekday
        data.sort((a, b) => {
            return a.weekday - b.weekday;
        });

        //push data to array
        data.forEach(weekday => {
            countData.push(weekday.count);
            activeTime.push(Math.floor(weekday.active_minutes));
            inactiveTime.push(Math.floor(weekday.inactive_minutes));
        });
        
        return {
            x: xAxis,
            count: countData,
            active: activeTime,
            inactive: inactiveTime
        }
    }

    function getData(){
        const url = '/api/steps/breakdown/?groupby=weekly';

        return makeRequest('GET', url).then(result => {
            let data = JSON.parse(result);
            
            return formatData(data);
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
                    data.count,
                    data.active,
                    data.inactive
                ],
                type: 'bar',
                groups: [
                    ['active', 'inactive']
                ],
                names: {
                    active: 'active time',
                    inactive: 'inactive time'
                },
                axes: {
                    count: 'y',
                    inactive: 'y2'
                },
                colors: {
                    steps: '#4A2B4B',
                    active: '#b94305',
                    inactive: '#a9a9a9'
                }
            },
            axis: {
                y: {
                    label: 'steps'
                },
                y2: {
                    label: 'Minutes',
                    show: true
                },
                x: {
                    type: 'category',
    
                }
            },
   
            legend: {
                hide: false
            }
        });
    }

    getData().then(data => {
        createChart('#weekday_breakdown', data);
    })
})();

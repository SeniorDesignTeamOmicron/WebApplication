var pressureBreakdown = (function () {
    const endpoint = '/api/steps/pressure/'
    const today = new Date();
    const url = `${endpoint}?date=${today.getMonth()+1}-${today.getDate()}-${today.getFullYear()}`;

    function setSensorText(dateRange, shoe, sensor, pressureData) {
        if(pressureData.length) {
            if(sensor == 'bottom'){
                document.querySelectorAll(`.${dateRange} > .shoe.${shoe} > .bottom-sensor`)[0].innerText = (pressureData[0].location == 'B'? pressureData[0].avg_pressure : pressureData[1].avg_pressure).toFixed(2);
            }else if(sensor == 'top'){
                document.querySelectorAll(`.${dateRange} > .shoe.${shoe} > .top-sensor`)[0].innerText = (pressureData[0].location == 'T'? pressureData[0].avg_pressure : pressureData[1].avg_pressure).toFixed(2);
            }
        }
    }

    return makeRequest('GET', url).then(result => {
        let data = JSON.parse(result);
        
        let pressureData = data.pressure.past_month.left_shoe;
        setSensorText('month', 'left', 'top', pressureData)
        setSensorText('month', 'left', 'bottom', pressureData)
        
        pressureData = data.pressure.past_month.right_shoe;
        setSensorText('month', 'right', 'top', pressureData)
        setSensorText('month', 'right', 'bottom', pressureData)

        pressureData = data.pressure.past_week.left_shoe;
        setSensorText('week', 'left', 'top', pressureData)
        setSensorText('week', 'left', 'bottom', pressureData)

        pressureData = data.pressure.past_week.right_shoe;
        setSensorText('week', 'right', 'top', pressureData)
        setSensorText('week', 'right', 'bottom', pressureData)

        pressureData = data.pressure.past_day.left_shoe;
        setSensorText('day', 'left', 'top', pressureData)
        setSensorText('day', 'left', 'bottom', pressureData)

        pressureData = data.pressure.past_day.right_shoe;
        setSensorText('day', 'right', 'top', pressureData)
        setSensorText('day', 'right', 'bottom', pressureData)
    });
})()
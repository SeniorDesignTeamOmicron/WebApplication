var weekActivity = (function () {
    let today = new Date(2018,6,15);
    let sunday = getWeekStart(today);
    let saturday = getWeekEnd(today);
    let dates = [];

    function getWeekStart(today) {
        let tempDate = new Date(today.valueOf());
        tempDate.setDate(today.getDate() - today.getDay());
        return tempDate;
    }

    function getWeekEnd(today) {
        let tempDate = new Date(today.valueOf());
        tempDate.setDate(today.getDate() + (6 - today.getDay()));
        return tempDate;
    }

    function setWeekTitle(){
        startDateHeader = document.getElementById('start_date');
        endDateHeader = document.getElementById('end_date');

        startDateText = `${months[sunday.getMonth()]} ${sunday.getDate()}, ${sunday.getFullYear()}`;
        endDateText = `${months[saturday.getMonth()]} ${saturday.getDate()}, ${saturday.getFullYear()}`;

        startDateHeader.innerText = startDateText;
        endDateHeader.innerText = endDateText;
    }

    function Weekday(weekday) {
        let date = new Date(sunday.valueOf());
        date.setDate(date.getDate() + weekday);

        let cssClass = `.${weekdays[date.getDay()].toLowerCase()}`;

        function toString(){
            return `${date.getMonth()+1}-${date.getDate()}-${date.getFullYear()}`
        }

        function formatData(data) {
            let left = data.goal - data.steps;
        
            return {
                steps: data.steps,
                left: left,
                percent: data.percent
            }
        }

        function getData() {
            const url = '/api/steps/summary/?date=';

            return makeRequest('GET', `${url}${toString()}`).then(result => {
                let data = JSON.parse(result);
                return formatData(data);
            });
        }

        function renderData() {
            return getData().then(data => {
                let monthLabel = document.querySelector(`${cssClass} > .month`);
                let dateLabel = document.querySelector(`${cssClass} > .date`);

                monthLabel.innerText = months[date.getMonth()];
                dateLabel.innerText = date.getDate();
            });
        }

        return {
            renderData: renderData
        }
    }

    setWeekTitle();

    for(let i = 0; i < 7; i++) {
        let weekday = new Weekday(i);
        weekday.renderData();
        dates.push(weekday);
    }
})()


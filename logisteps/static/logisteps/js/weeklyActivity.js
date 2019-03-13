var weekActivity = (function () {
    let today, sunday, saturday, dates;

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

        const weekday_str = weekdays[date.getDay()];

        let cssClass = `.${weekdays[date.getDay()].toLowerCase()}`;

        function toString(){
            return `${date.getMonth()+1}-${date.getDate()}-${date.getFullYear()}`
        }

        function getData() {
            const url = '/api/steps/summary/?date=';

            return makeRequest('GET', `${url}${toString()}`).then(result => {
                let data = JSON.parse(result);
                return data;
            });
        }

        function renderDateHeader() {
            let dateLabel = document.querySelector(`${cssClass} > .date`);

            dateLabel.innerText = date.getDate();
        }

        function renderActivityProgress(data) {
            const inactive_min = data.inactive_time.hours * 60 + data.inactive_time.minutes;
            const active_time = (24 * 60) - inactive_min;
            const percent_active = active_time / (24 * 60) * 100;

            var chart = c3.generate({
                bindto: `#${weekday_str.toLowerCase()}_graph`,
                data: {
                  columns: [
                    ['Active Time', percent_active],
                    ['Goal Progress', data.percent]
                  ],
                  colors: {
                  'Active Time':'#b94305',
                  'Goal Progress':'#4A2B4B',
                  },
                  type: 'gauge',
                  labels: false
                },
                size: {
                  height: 200,
                  width: 165
                },
                padding: {
                    bottom: 10
                },
                    tooltip: {
                        format: {
                            value: function (value) {
                                var p = Math.max(0, d3.precisionFixed(0.05)),
                                f = d3.format("." + p + "%");
                                return f(value/100);
                            }
                        }
                    }
                
              });
        }

        function renderData() {
            return getData().then(data => {
                renderDateHeader();
                renderActivityProgress(data);
            });
        }

        return {
            renderData: renderData
        }
    }

    function displayWeek(date) {
        today = date;
        sunday = getWeekStart(today);
        saturday = getWeekEnd(today);
        dates = [];

        document.getElementById('activity_loader').style.visibility="visible";
        setWeekTitle();
        for(let i = 0; i < 7; i++) {
            let weekday = new Weekday(i);
            
            dates.push(weekday.renderData());
        }
        Promise.all(dates).then(() => {
            document.getElementById('activity_loader').style.visibility="hidden";
        })
    }

    var picker = new Pikaday({
        field: document.getElementById('datepicker'),
        trigger: document.getElementById('datepicker-button'),
        onSelect: displayWeek
    });
    displayWeek(new Date());
})()


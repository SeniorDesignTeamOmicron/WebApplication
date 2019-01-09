function makeRequest (method, url) {
    return new Promise(function (resolve, reject) {
        var xhr = new XMLHttpRequest();
        xhr.open(method, url);
        xhr.onload = function () {
        if (this.status >= 200 && this.status < 300) {
            resolve(xhr.response);
        } else {
            reject({
            status: this.status,
            statusText: xhr.statusText
            });
        }
        };
        xhr.onerror = function () {
        reject({
            status: this.status,
            statusText: xhr.statusText
        });
        };
        xhr.send();
    });
}

function loadRecentData(){
    const summaryEndpoint = '/api/steps/summary/?date=';
    const today = new Date(2018,6,19);

    function formatDonutData(dataString) {
        let data = JSON.parse(dataString);
        let left = data.goal - data.steps;
        
        return {
            steps: data.steps,
            left: left,
            percent: data.percent
        }
    }

    function createChart(id, stepData) {
        c3.generate({
            bindto: id,
            data: {
                json: [stepData],
                type : 'donut',
                keys: {
                    value: ['steps', 'left'],
                },
                colors: {
                    steps: '#ff0000',
                    left: '#ffffff'
                },
                onclick: function (d, i) { console.log("onclick", d, i); },
                onmouseover: function (d, i) { console.log("onmouseover", d, i); },
                onmouseout: function (d, i) { console.log("onmouseout", d, i); },
            },
            legend: {
                hide: true
            },
            donut: {
                title: stepData.percent.toPrecision(2) + '%',
                label: {
                    show: false
                }
            }
        });
    }

    makeRequest('GET', `${summaryEndpoint}${today.getMonth()+1}-${today.getDate()}-${today.getFullYear()}`).then(result => {
        let data = formatDonutData(result);
        createChart('#recent1', data);
    });

    makeRequest('GET', `${summaryEndpoint}${today.getMonth()+1}-${today.getDate()-1}-${today.getFullYear()}`).then(result => {
        let data = formatDonutData(result);
        createChart('#recent2', data);
    });
}
var recentStepSummaryView = (function loadRecentData(){
    const summaryEndpoint = '/api/steps/summary/?date=';
    const today = new Date();

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
            size: {
                 width: 350,
                 height: 350
            },
            data: {
                json: [stepData],
                type : 'donut',
                keys: {
                    value: ['steps', 'left'],
                },
                colors: {
                    steps: '#49274A',
                    left: '#D3D3D3'
                },
            },
            legend: {
                hide: true
            },
            donut: {
                title: 'Progress: ' + stepData.percent.toFixed(2) + '%',
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
})();
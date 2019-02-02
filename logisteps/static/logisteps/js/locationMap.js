var initMap = function () {
    const today = new Date(2018,6,15);
    const endPoint = '/api/steps/location/';
    const url = `${endPoint}?date=${today.getMonth()+1}-${today.getDate()}-${today.getFullYear()}`

    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 3,
        center: { lat: 0, lng: -180 },
        mapTypeId: 'terrain'
    });

    function formatData(data) {
        let locations = data.locations;
        let coordinates = [];

        locations.map((dataPoint) => {
            coordinates.push({
                lat: dataPoint.latitude,
                lng: dataPoint.longitude
            });
        });

        return coordinates;
    }

    return makeRequest('GET', url).then(result => {
        const data = JSON.parse(result);
        
        const coordinates = formatData(data);
        const dailyMovement = new google.maps.Polyline({
            path: coordinates,
            geodesic: true,
            strokeColor: '#FF0000',
            strokeOpacity: 1.0,
            strokeWeight: 2
        });
        dailyMovement.setMap(map);
    });
}
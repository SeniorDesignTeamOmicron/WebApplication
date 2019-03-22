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
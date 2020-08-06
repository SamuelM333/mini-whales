let ws = new WebSocket('ws://' + document.URL.replace("http://", ""));
let log_container = document.getElementById("logs");

ws.onopen = function (event) {
    ws.send(JSON.stringify({type: "onopen", data: "Connected!"}));
};

ws.onmessage = function (event) {
    log_container.innerHTML += event.data;
};

var videoTitle = document.getElementById("video-title")
var histoCount = []
var timeouts = []

if (iTag === undefined || iTag === null) {
    var iTag = document.querySelector("#ivideo-title")
}

function create_level_valid() {
    iTag.classList.add("fa-solid", "fa-check", "text-success");
}

function del_level_valid() {
    iTag.classList.remove("fa-solid", "fa-check", "text-success");
}

lines.includes(lineNb) ? create_level_valid() : del_level_valid()

histoCount.push(lineNb)

function getTip(tips) {
    var tip = JSON.stringify(tips);
    tip = JSON.parse(tip);

    const newData = Object.keys(tip).reduce(function (obj, key) {
        obj[tip[key]] = key;
        return obj;
    }, {});
    return newData
}

tip = getTip(tips)

var timeout = setTimeout(stopVideo, timeouts[lineNb]);

for (let i = 0; i < ts.length - 1; i++) {
    result = ((ts[i + 1] - ts[i]) * 1000) - 200
    timeouts.push(Number(result.toFixed(2)))
}

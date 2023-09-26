let graphDuration = 60;
let updateFrequency = 1;

let contents = "";
let contentString = "";
let recent = [];
let header = [];

// retrieve the CSV data at regular intervals [DEPRECATED]
// function getData(){
//     $.get("../ev_data/temp.csv", function(data) {
//         contentString = data;
//     });
// }

function doGET(path, callback) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            // The request is done; did it work?
            if (xhr.status == 200) {
                // ***Yes, use `xhr.responseText` here***
                callback(xhr.responseText);
            } else {
                // ***No, tell the callback the call failed***
                callback(null);
            }
        }
    };
    xhr.open("GET", path);
    xhr.send();
}

function handleFileData(fileData) {
    if (!fileData) {
        console.log("XML HTTP Request Failed");
        return;
    }
    // Use the file data
    contentString = fileData;
}

let cache = [];

// in seconds at updateFrequency rows per second
let cacheSize = 60;
let lastRow = "";

let graphSize = graphDuration * updateFrequency;

setInterval(update, 1000/updateFrequency);
//update();

// createWindow("Graph", "V");

function update(){
    brainCells -= Math.floor(Math.random() * 20);
    //getData();
    doGET("../ev_data/temp.csv", handleFileData);
    let contents = contentString;
    graphSize = graphDuration * updateFrequency;

    // split away the first line of the CSV file for column names
    contents = contents.split("\r\n");
    header = contents[0].split(",");

    // remove header line so it doesn't affect the graph
    // and last line because it is always empty
    contents.shift();
    contents.pop();

    let newContents = [];
    for (let i = contents.length - 1; i > 0; i--){
        if(contents[i] != cache[cache.length - 1]){
            newContents.push(contents[i]);
        }else{
            break;
        }
    }

    for(let i = newContents.length - 1; i > 0; i--){
        cache.push(newContents[i]);
        if(cache.length > cacheSize * updateFrequency){
            cache.shift();
        }
    }

    lastRow = contents[contents.length - 1];

    // get only the last graphDuration seconds or less of the data
    if(cache.length > graphSize){
        recent = cache.slice(-graphSize);
    }else{
        recent = structuredClone(cache);
    }

    for(let i = 0, l = recent.length; i < l; i++){
        recent[i] = recent[i].split(",");
    }

    // need any graphs?
    for(let i = 0, l = graphs.length; i < l; i++){
        renderGraph(graphs[i]);
    }

    for(let i = 0; i < analyticsWindows.length; i++){
        updateAnalytics(analyticsWindows[i]);
    }
}

function updateAnalytics(analyticsWindow){
    try{
        let amphPerS = ((15.5 - parseFloat(recent[recent.length - 31][1])) - (15.5 - parseFloat(recent[recent.length - 1][1])));
        let minutesRemaining = (((15.5 - parseFloat(recent[recent.length - 1][1])) / amphPerS) / 60).toFixed(2);

        analyticsWindow.innerHTML = "<p><b>" + minutesRemaining + " minutes remaining</b></p>";
        analyticsWindow.innerHTML += "<p><b>using " + (amphPerS * 60).toFixed(3) + " amp-hours per minute</b></p>";
        analyticsWindow.innerHTML += "<p><b>team collective brain cells: " + brainCells + "</b></p>";
    }catch{
        analyticsWindow.innerHTML = "<p><b>The software must run for 30 seconds before an accurate estimation can be provided.</b></p>";
    }
}

const average = array => array.reduce((a, b) => a + b) / array.length;

function renderGraph(graph){

    let canvas = graph[1];
    let properties = graph[2];
    let sampleLength = properties.duration * updateFrequency;
    let width = canvas.width;
    let height = canvas.height;
    let interval = width / sampleLength;
    let progress = 0;

    // TODO: custom min and max, styles
    // Cut off first seconds or so of graph for clean scroll

    let sample = []

    if(sampleLength >= recent.length){
        sample = structuredClone(recent);
    }else{
        sample = recent.slice(-sampleLength);
    }

    let ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, width, height);

    //implement scale
    ctx.lineCap = "round";
    ctx.lineWidth = properties.lineThickness;
    ctx.strokeStyle="rgba(0, 0, 0, 1)";
    canvas.style.backgroundColor = properties.backgroundColor;

    if(graph[2].isGauge){
        for (let j = 0, jl = header.length; j < jl; j++){
            if(graph[0] != header[j]) {continue;}
            graph[3].innerHTML = graph[0] + " | " + sample[sample.length - 1][j];

            let filtered = [];
            for (let k = 0, kl = sample.length; k < kl; k++){
                filtered.push(parseFloat(sample[k][j]));
            }

            var centerX = width / 2;
            var centerY = height / 2;
            var r = (Math.min(width, height) / 2) * 0.8;
            var ratio = properties.max - properties.min;

            // gauge
            ctx.strokeStyle="rgba(0, 0, 0, 0.4)";
            ctx.beginPath();
            ctx.arc(centerX, centerY, r, 0.75*Math.PI, 0.25*Math.PI);
            ctx.stroke();

            ctx.strokeStyle = properties.color;

            ctx.beginPath();
            ctx.arc(centerX, centerY, r, 0.75*Math.PI, 0.75*Math.PI + (1.5*Math.PI) * (sample[sample.length - 1][j] / ratio));
            ctx.stroke();

            // text
            ctx.textAlign = "center";
            ctx.font = "bold 30px Monospace";

            ctx.fillText(sample[sample.length - 1][j], centerX, centerY);
            ctx.fillText("Mean", centerX, centerY + 48);
            ctx.fillText(Math.round(average(filtered) * 100) / 100, centerX, centerY + 72);

            return;
        }
    }
    for (let j = 0, jl = header.length; j < jl; j++){
        if(graph[0] != header[j]) {continue;}
        let stepX = properties.stepX;
        let stepY = properties.stepY;

        let filtered = [];
        for (let k = 0, kl = sample.length; k < kl; k++){
            filtered.push(parseFloat(sample[k][j]));
        }

        let min = Math.min.apply(Math, filtered);
        let max = Math.max.apply(Math, filtered);

        graph[3].innerHTML = graph[0] + " | " + sample[sample.length - 1][j];

        let range = max - min;
        let ratio = height / 2 / range;
        let adjustedMin = height / 4;

        let tMin = 0;
        let tMax = 0;
        if(properties.relativeTime){
            tMin = -properties.duration;
            tMax = 0;
        }else{
            tMin = parseInt(sample[0][0]);
            tMax = parseInt(sample[sample.length - 1][0]);
        }
        let rangeX = tMax - tMin;
        let ratioX = width / rangeX;

        ctx.strokeStyle="rgba(0, 0, 0, 0.25)";
        ctx.font = "26px Monospace";

        let start = nextMultiple(tMin, properties.stepX);
        let end = previousMultiple(tMax, properties.stepX);

        for(let i = start; i <= end; i += properties.stepX){
            let pos = ((i-tMin) * ratioX);
            ctx.beginPath();
            ctx.moveTo(pos, 0);
            ctx.lineTo(pos, height);
            ctx.stroke();
            ctx.fillText(i, pos + 2, height - 2);
        }

        start = nextMultiple(min, properties.stepY);
        end = previousMultiple(max, properties.stepY);
        difference = end - start;

        for(let i = start - difference/2; i <= end + difference/2; i += properties.stepY){
            let pos = height - (((i-min) * ratio) + adjustedMin);
            ctx.beginPath();
            ctx.moveTo(0, pos);
            ctx.lineTo(width, pos);
            ctx.stroke();
            ctx.fillText(i, 0, pos - 2);
        }

        ctx.strokeStyle = properties.color;
        ctx.beginPath();
        for (let k = 0, kl = sample.length; k < kl; k++){
            if(k == 0){
                ctx.moveTo(progress, height - (((sample[k][j]-min) * ratio) + adjustedMin));
                // console.log(height - (((sample[k][j]-min) * ratio)));
            }else{
                ctx.lineTo(progress, height - (((sample[k][j]-min) * ratio) + adjustedMin));
                //ctx.stroke();
            }
            progress += interval;
        }
        ctx.stroke();
    }
}

function drawLine(ctx, x1, y1, x2, y2){
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
}

//x is the step size
function closestMultiple(n, x)
{  
    n = n + x/2;
    n = n - (n%x);
    return n;
}

function previousMultiple(n, x)
{  
    n = n - (n%x);
    return n;
}

function nextMultiple(n, x)
{  
    n = n - (n%x) + x;
    return n;
}

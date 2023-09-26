let graphs = [];
let analyticsWindows = [];
let brainCells = 2937491845;
// let graph = document.createElement('div');
// let canvas = document.createElement('canvas');
// canvas.style.backgroundColor = 'lightgray';
// graph.appendChild(canvas);
let graphTemplate = document.getElementById('graph');
let propertiesTemplate = document.getElementById('properties');
let gaugePropertiesTemplate = document.getElementById('gaugeProperties');
let analyticsTemplate = document.getElementById('analytics');
let luigiTemplate = document.getElementById('luigi');
let usedIDs = 0;
let zIndices = 0;

const observer = new ResizeObserver(entries => {
    entries.forEach(entry => {
        let canvas = entry.target.getElementsByTagName('canvas')[0];
        canvas.width = entry.contentRect.width * 2;
        canvas.height = (entry.contentRect.height - entry.target.children[0].clientHeight) * 2;
        canvas.style.width = entry.contentRect.width + "px";
        canvas.style.height = (entry.contentRect.height - entry.target.children[0].clientHeight) + "px";
        for(let i = 0; i < graphs.length; i++) {
            if(graphs[i][1] == canvas){
                renderGraph(graphs[i]);
            }
        }
    })
})

function graphProperties(){
    this.isGauge = false;
    this.id = 0;
    this.name = "";
    this.duration = 30;
    this.min = 0;
    this.max = 100;
    this.scale = 1;
    this.color = "rgba(0, 71, 171, 1)";
    this.lineThickness = 4;
    this.backgroundColor = "rgb(255, 255, 255)";
    this.axisProportions = 0;
    this.relativeTime = true;
    this.stepX = 10;
    this.stepY = 4;
    this.minorX = 1;
    this.minorY = 1;
}

let recentGraph;

function createWindow(type, variant) {
    let elem = document.createElement('div')
    elem.style = `position: absolute; border-radius: 6px; overflow: hidden;
        box-shadow: 6px 6px 8px rgb(42, 42, 42, 0.25); resize: both;
        min-width: 200px; min-height: 160px; rotate: 0deg;`
    elem.classList.add('window');

    if(type == "Graph"){
        elem.append(graphTemplate.content.cloneNode(true));
        elem.id = "window_" + usedIDs;
        let topbar = elem.children[0];
        topbar.id = "window_" + usedIDs + "_header"

        topbar.innerHTML = type;

        graphs.push([variant, elem.getElementsByTagName('canvas')[0], new graphProperties(), topbar]);
        graphs[graphs.length - 1][2].id = usedIDs;
        graphs[graphs.length - 1][2].name = variant;

        eval(`
            topbar.addEventListener("contextmenu", function(e){
                e.preventDefault();
                recentGraph = ` + usedIDs + `;
                contextMenu("cm_graph");
            })
        `)
    }if(type == "Gauge"){
        elem.append(graphTemplate.content.cloneNode(true));
        elem.id = "window_" + usedIDs;
        let topbar = elem.children[0];
        topbar.id = "window_" + usedIDs + "_header"

        topbar.innerHTML = type;

        var props = new graphProperties();
        props.isGauge = true;
        props.lineThickness = "16";
        graphs.push([variant, elem.getElementsByTagName('canvas')[0], props, topbar]);
        graphs[graphs.length - 1][2].id = usedIDs;
        graphs[graphs.length - 1][2].name = variant;

        eval(`
            topbar.addEventListener("contextmenu", function(e){
                e.preventDefault();
                recentGraph = ` + usedIDs + `;
                contextMenu("cm_graph");
            })
        `)
    }else if(type == "Properties"){
        let prop = propertiesById(recentGraph);
        if(prop.isGauge){
            elem.append(gaugePropertiesTemplate.content.cloneNode(true));
        }else{
            elem.append(propertiesTemplate.content.cloneNode(true));
        }
        elem.id = "window_" + usedIDs;
        let topbar = elem.children[0];
        topbar.id = "window_" + usedIDs + "_header";

        topbar.innerHTML = "Properties of \'" + prop.name + "\'";

        let paraFields = elem.getElementsByTagName("div")[0].getElementsByTagName("p");
        let inputFields = [];
        for(let i = 0; i < paraFields.length; i++) {
            inputFields.push(paraFields[i].getElementsByTagName("input")[0]);
        }

        if(prop.isGauge){
            inputFields[0].value = prop.min.toString();
            inputFields[1].value = prop.max.toString();
            inputFields[2].value = prop.duration.toString();
            inputFields[3].value = prop.color.toString();
            inputFields[4].value = prop.backgroundColor.toString();
            inputFields[5].value = prop.lineThickness.toString();
        }else{
            inputFields[0].value = prop.stepX.toString();
            inputFields[1].value = prop.stepY.toString();
            inputFields[2].value = prop.duration.toString();
            inputFields[3].checked = prop.relativeTime;
            inputFields[4].value = prop.color.toString();
            inputFields[5].value = prop.backgroundColor.toString();
            inputFields[6].value = prop.lineThickness.toString();
        }

        elem.getElementsByTagName('span')[0].innerHTML = recentGraph;
    }else if(type == "Analytics"){
        elem.append(analyticsTemplate.content.cloneNode(true));
        elem.id = "window_" + usedIDs;
        let topbar = elem.children[0];
        topbar.id = "window_" + usedIDs + "_header";
        analyticsWindows.push(elem.children[3]);
        topbar.innerHTML = "Analytics";

        elem.getElementsByTagName('span')[0].innerHTML = recentGraph;
    }else if(type == "luigi"){
        elem.style = `position: absolute; border-radius: 6px; overflow: hidden;
        box-shadow: 6px 6px 8px rgb(42, 42, 42, 0.25); resize: both;
        min-width: 300px; min-height: 240px; rotate: 0deg;`
        elem.append(luigiTemplate.content.cloneNode(true));
        elem.id = "window_" + usedIDs;
        let topbar = elem.children[0];
        topbar.id = "window_" + usedIDs + "_header";
        topbar.innerHTML = "Moral Support";
        elem.style.transition = "top 0.2s, left 0.2s";

        elem.getElementsByTagName('span')[0].innerHTML = recentGraph;

        eval(`
            topbar.addEventListener("contextmenu", function(e){
                e.preventDefault();
                recentGraph = ` + usedIDs + `;
                contextMenu("cm_luigi");
            })
        `)
    }

    if(type == "luigi" && recentGraph != -1){
        graphById(recentGraph).appendChild(elem);
    }else{
        document.body.children[1].appendChild(elem);
    }
    
    elem.style.top = "100px";
    elem.style.left = "100px";
    elem.style.zIndex = usedIDs;
    if(type == "Graph" || type == "Gauge"){
        observer.observe(elem);
    }
    dragElement(elem);
    elem.addEventListener("mousedown", function(){
        zIndices++;
        elem.style.zIndex = zIndices;
    });

    usedIDs++;
}

function propertiesById(id){
    for(let i = 0; i < graphs.length; i++) {
        if(graphs[i][2].id == id){
            return graphs[i][2];
        }
    }
}

function graphById(id){
    for(let i = 0; i < graphs.length; i++) {
        if(graphs[i][2].id == id){
            return graphs[i][1];
        }
    }
}

function makeTransparent(){
    if(graphById(recentGraph).parentElement.style.opacity == "0.5"){
        graphById(recentGraph).parentElement.style.opacity = "1";
    }else{
        graphById(recentGraph).parentElement.style.opacity = "0.5";
    }
}

function rotate(amount, isAdding){
    if(isAdding){
        graphById(recentGraph).parentElement.style.rotate = (parseInt(graphById(recentGraph).parentElement.style.rotate.slice(0, -3)) + amount) + "deg";
    }else{
        graphById(recentGraph).parentElement.style.rotate = amount + "deg";
    }
}

function dragElement(elmnt)
{
    var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    if (document.getElementById(elmnt.id + "_header")) {
      // if present, the header is where you move the DIV from:
      document.getElementById(elmnt.id + "_header").onmousedown = dragMouseDown;
    } else {
      // otherwise, move the DIV from anywhere inside the DIV:
      elmnt.onmousedown = dragMouseDown;
    }
  
    function dragMouseDown(e) {
      e = e || window.event;
      e.preventDefault();
      // get the mouse cursor position at startup:
      pos3 = e.clientX;
      pos4 = e.clientY;
      document.onmouseup = closeDragElement;
      // call a function whenever the cursor moves:
      document.onmousemove = elementDrag;
      elmnt.style.transition = "";
    }
  
    function elementDrag(e) {
      e = e || window.event;
      e.preventDefault();
      // calculate the new cursor position:
      pos1 = pos3 - e.clientX;
      pos2 = pos4 - e.clientY;
      pos3 = e.clientX;
      pos4 = e.clientY;
      // set the element's new position:
      elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
      elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
    }
  
    function closeDragElement() {
      // stop moving when mouse button is released:
      document.onmouseup = null;
      document.onmousemove = null;
      elmnt.style.transition = "top 0.2s, left 0.2s";
    }
}

document.addEventListener("click", function(event) {
    if(event.target.className == "context"){return;}
    document.getElementById("contextMenu").style.display = "none";
});

let mouseX = 0;
let mouseY = 0;

document.addEventListener("mousemove", function(e){
    mouseX = e.clientX;
    mouseY = e.clientY;
});

let cm = document.getElementById("contextMenu");
function contextMenu(template){
    cm.style.display = "block";
    cm.style.left = mouseX + "px";
    cm.style.top = mouseY + "px";
    cm.innerHTML = "";
    cm.appendChild(document.getElementById(template).content.cloneNode(true));
}
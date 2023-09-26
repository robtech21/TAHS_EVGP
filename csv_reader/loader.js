function loadScript(url, callback){

    var script = document.createElement("script")
    script.type = "text/javascript";

    if (script.readyState){  //IE
        script.onreadystatechange = function(){
            if (script.readyState == "loaded" ||
                    script.readyState == "complete"){
                script.onreadystatechange = null;
                callback();
            }
        };
    } else {  //Others
        script.onload = function(){
            callback();
        };    }

    script.src = url;
    document.getElementsByTagName("head")[0].appendChild(script);
}

loadScript("interface.js", function(){
    loadScript("script.js", function(){
        console.log("Loaded Successfully");
    })
});
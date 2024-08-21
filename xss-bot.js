var page = require('webpage').create();
var host = "vpwa_main_3000";
var url = "https://"+host+":6177/posts/";
var timeout = 2000;
phantom.addCookie({
    'name': 'session',
    'value': 'FLAG{0op$_c00k13_w17h0u7_h77p_0n1y?}',
    'domain': host,
    'path': '/',
    'httponly': false
});
page.onNavigationRequested = function(url, type, willNavigate, main) {
    console.log("[URL] URL="+url);
};
page.settings.resourceTimeout = timeout;
page.onResourceTimeout = function(e) {
    setTimeout(function(){
        console.log("[INFO] Timeout")
        phantom.exit();
    }, 1);
};
for (i=1;i<5;i++) {
    page.open(url+i, function(status) {
        console.log("[INFO] rendered page");
        setTimeout(function(){
            phantom.exit();
        }, 1);
    });
}
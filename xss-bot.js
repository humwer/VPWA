var page = require('webpage').create();
var system = require('system');
var host = system.args[1];
var post_num = system.args[2];
var url = "http://"+host+":6177/posts/"+post_num;
var timeout = 5000;
var seconds = 5000;

phantom.addCookie({
    'name': 'BotCookie',
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
    }, seconds);
};

page.open(url, function(status) {
    console.log("[INFO] rendered page");
    setTimeout(function(){
        phantom.exit();
    }, seconds);
});
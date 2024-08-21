var page = require('webpage').create();
var system = require('system');
var host = system.args[1];
var url = "https://"+host+":6177/posts/";
var timeout = 5000;
var seconds = 5;

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
    }, seconds);
};

page.open(url+1, function(status) {
    console.log("[INFO] rendered page");
    setTimeout(function(){
        phantom.exit();
    }, seconds);
});

page.open(url+2, function(status) {
    console.log("[INFO] rendered page");
    setTimeout(function(){
        phantom.exit();
    }, seconds);
});

page.open(url+3, function(status) {
    console.log("[INFO] rendered page");
    setTimeout(function(){
        phantom.exit();
    }, seconds);
});

page.open(url+4, function(status) {
    console.log("[INFO] rendered page");
    setTimeout(function(){
        phantom.exit();
    }, seconds);
});
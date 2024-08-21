#!/bin/bash

while sleep 1
do
	for i in {1..4}
	do
	  phantomjs --ignore-ssl-errors=true --local-to-remote-url-access=true --web-security=false --ssl-protocol=any /bot/xss-bot.js $name_service ${i};
	done;
done;

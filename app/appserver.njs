#!/usr/bin/env node

var express = require('express');
var app = express();

http_port = 8076;
root_dir = __dirname + "/assets/www/";

app.get('/*', function(req, res) {
	req_file = root_dir + req.path;
	res.sendfile(req_file);
	console.log('path: ', req_file);
});


var server = app.listen(http_port);
console.log("# Web Server listening on port " + server.address().port + " for " + root_dir);

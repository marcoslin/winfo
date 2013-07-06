angular.module('WinfoWeb', ['ui.bootstrap','Nav.directives','dataServices'])
.config(function ($routeProvider) {
	'use strict';
	$routeProvider
		.when('/', { templateUrl: 'views/main.html', controller: 'MainCtrl', navTab: "home" })
		.when('/info', { templateUrl: 'views/info.html', controller: 'MainCtrl', navTab: "info" })
		.when('/profile', { templateUrl: 'views/profile.html', controller: 'MainCtrl', navTab: "profile" })
		.otherwise({ redirectTo: '/' });
});

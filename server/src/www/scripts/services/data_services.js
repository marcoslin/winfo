angular.module("dataServices", ['ngResource'])
	.factory('User', function ($resource) {
		'use strict';
		var actions = {
			'query': {method:'GET', isArray:true},
			'get': {method:'GET'},
			'save': {method:'PUT'},
			'add': {method:'POST', params: {user_id: "add"}},
			'delete': {method:'DELETE'}
		};
        return $resource("/d/user/:user_id", {}, actions);
    })
	;
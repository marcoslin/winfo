angular.module('Z1kApp')
.controller("MainCtrl", function ($scope, nav) {
	
	$scope.goToPage = nav.goToPage;
});
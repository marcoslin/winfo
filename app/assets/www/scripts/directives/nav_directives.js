angular.module('Nav.directives', ['PhoneGap.services'])
.controller('mainActionBarCtrl', function ($scope, $location, nav, $log) {
	var active_class = "topcoat-icon-button is-active",
		inactive_class = "topcoat-icon-button--quiet";
	
	// Set the ActionBar's status based on current path
	function setActionBarStatus(pageName) {
		var profile_class = inactive_class,
			nearby_class = inactive_class,
			livebook_class = inactive_class,
			settings_class = inactive_class;
	
		if (pageName === "/profile") {
			profile_class = active_class;
		}  else if  (pageName === "/nearby") {
			nearby_class = active_class;
		} else if  (pageName === "/livebook") {
			livebook_class = active_class;
		} else if  (pageName === "/settings") {
			settings_class = active_class;
		}
		
		$scope.icon_class = {
			profile: profile_class,
			nearby: nearby_class,
			livebook: livebook_class,
			settings: settings_class
		};
	}
	setActionBarStatus($location.path());

	// Navigation options
	$scope.navigateTo = nav.navigateTo;
	$scope.goToPage = nav.goToPage;
	
})
.directive('mainActionBar', function (nav) {
	return {
		restrict: 'E',
		controller:'mainActionBarCtrl',
		templateUrl: 'scripts/directives/templates/mainActionBar.html'
	};
});
angular.module('Nav.directives', ['restAuthServices'])
.controller('mainNavigationCtrl', function ($scope, $dialog, $location, $route, Authenticate, $log) {
	$scope.main_button_action = "Login";
	
	// Private Functions 
	function setFormStatus() {
		// Set login status
		var user_name = Authenticate.get_username();
		if (user_name) {
			$scope.user_name = user_name;
			$scope.main_button_action = "Logout";
		} else {
			login();
			$scope.main_button_action = "Login";
		}
		// Set navigation
		var navclass = { home: "", info: "", profile: "" },
			navtab = $route.current.navTab;
		if ( navtab === "info" ) {
			navclass.info = "active";
		} else if ( navtab === "profile" ) {
			navclass.profile = "active";
		} else {
			navclass.home = "active";
		}
		$scope.navclass = navclass;
	}
	
	function login() {
		var d = $dialog.dialog({ dialogFade: true });
		d.open('scripts/directives/templates/login.html', 'LoginCtrl').then(function (data) {
			if ( data === "Ok" ) {
				setFormStatus();
			}
		});
	}
	
	function logout() {
		Authenticate.logout();
		$scope.user_name = "";
		$location.path("/");
		$scope.main_button_action = "Login";
	}
	
	// Navigation
	$scope.goToPage = function (page) {		
		$location.path(page);
	};
	
	// Button Action
	$scope.mainButtonAction = function () {
		if ( $scope.main_button_action === "Login" ) {
			login();
		} else {
			logout();
		}
	};
	
	
	// Initialize form
	setFormStatus();
	
})
.controller('LoginCtrl', function ($scope, dialog, Authenticate, User, $log) {
	// Set the form status for login
	$scope.setFormStatus = function (mode) {
		var fclass = {};
		if ( mode === "login" ) {
			fclass = {
				login_tab: "active",
				create_tab: "",
				login: "tab-pane active in",
				create: "tab-pane fade"
			};
		} else {
			fclass = {
				login_tab: "",
				create_tab: "active",
				login: "tab-pane fade",
				create: "tab-pane active in"
			};
		}
		$scope.form_mode = mode;
		$scope.fclass = fclass;
	};

	function success_handler() {
		dialog.close("Ok");
	}
	
	function fail_handler(error) {
		$log.error("Fail handler: ", error);
		var error_message;
		if ( error.data ) {
			error_message = error.data;
		} else {
			error_message = "Operation Failed.";
		}
		$scope.alert_status = {
			visible: true,
			message: error_message
		};
	}
	
	// Login submit
	$scope.loginSubmit = function () {
		Authenticate.login($scope.user_name, $scope.password, success_handler, fail_handler);
	};
	
	// Create submit
	$scope.createSubmit = function () {
		var user = new User();
		user.user_name = $scope.user_name;
		user.secure_passwd_hash = $scope.password;
		user.first_name = $scope.first_name;
		user.last_name = $scope.last_name;
		user.login_email = $scope.login_email;
		user.$add(
			function () {
				// Set the use as login and exit
				Authenticate.perform_login("New User Created.", $scope.user_name);
				success_handler();
			},
			fail_handler
		);
	};
	
	// Default the page to login
	$scope.setFormStatus("login");
})
.directive('mainNavivation', function () {
	return {
		restrict: 'E',
		controller:'mainNavigationCtrl',
		templateUrl: 'scripts/directives/templates/mainNavigation.html'
	};
});
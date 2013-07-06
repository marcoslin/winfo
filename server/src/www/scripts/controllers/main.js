

angular.module('WinfoWeb')
// Home Page and handle login
.controller('MainCtrl', function ($scope, $log) {
	//Pass
})
.controller('UserInfoCtrl', function ($scope, Authenticate, UserInfo, $log) {
	'use strict';
	var user_name = Authenticate.get_username();

	$scope.fst = {
		mode: "info",
		readOnly: false,
		saveEnabled: false
	};
		
	$scope.uinfo = UserInfo.get(
		{user_name: user_name},
		function () {
			// On success
			$scope.fst.saveEnabled = true;
		}
	);
	$log.log("uinfo: ", $scope.uinfo);
	
	$scope.addEmail = function () {
		var email = {type: null, email: null};
		$scope.uinfo.emails.push(email);
	};

	$scope.deleteEmail = function (index, email_id) {
		//$log.log("Deleting email index of " + index + " and id of " + email_id);
		if ( email_id ) {
			$scope.uinfo.deleted.emails.push(email_id);
		}
		// unsaved entry.  Simply remove from array
		$scope.uinfo.emails.splice(index, 1);
	};

	$scope.addAddress = function () {
		var address = {
			type: null,
			company_name: null,
			line1: null,
			line2: null,
			city: null,
			region: null,
			post_code: null,
			country: null,
		};
		$scope.uinfo.addresses.push(address);
	};

	$scope.deleteAddress = function (index, address_id) {
		if ( address_id ) {
			$scope.uinfo.deleted.addresses.push(address_id);
		}
		$scope.uinfo.addresses.splice(index, 1);
	};

	$scope.userInfoSubmit = function () {
		$scope.fst.saveEnabled = false;
		$scope.uinfo.$save(
			{user_name: user_name},
			function () {
				// success
				$scope.fst.saveEnabled = true;
			},
			function (error) {
				// error
				$scope.fst.saveEnabled = true;
			}
		);
	};
})
.controller('UserProfileCtrl', function ($scope, Authenticate, UserInfo, SharableProfile, $log) {
	'use strict';
	var user_name = Authenticate.get_username();
	
	// Profile Type drop down, as defined by SharableProfile.profile_type
	$scope.profile_types = [ "public", "private" ];
	
	$scope.fst = {
		mode: "profile",
		readOnly: true,
		saveEnabled: false
	};

	// Functions
	$scope.setSharedProfile = function (email_id) {
		$log.log("Email_id: ", email_id);
	};
	
	$scope.userInfoSubmit = function () {
		$log.log("uprofile: ", $scope.uprofile);
	};
	
	// Sourcing data
	$scope.profile_names = SharableProfile.query(
		{user_name: user_name},
		function () {
			$scope.profile_names.$then( function (result) {
				$log.log("Profile ", result.data);
				if ( result.data ) {
					// Query the first profile
					var profile_id = result.data[0].profile_id;
					$scope.uprofile = SharableProfile.get(
						{user_name: user_name, profile_id: profile_id}
						/*
						,function (result) {
							$scope.uprofile.$then ( function (result) {
								$log.log("uprofile: ", $scope.uprofile);
							});
						}
						*/
					);
				}
				
			});
		}
	);
	
	$scope.uinfo = UserInfo.get(
		{user_name: user_name},
		function () {
			// On success
			$scope.fst.saveEnabled = true;
		}
	);
	
	
})
;

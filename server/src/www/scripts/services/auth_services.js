angular.module('restAuthServices', ['ngResource', 'ngCookies'])

.service('Authenticate', function ($resource, $cookieStore) {
	'use strict';
	var self = this,
		priv_logginUser;
	
	// Loggin data
    var LoginService = $resource("/auth/:action", {}, {
        login: { method: "POST", params: {action: "login"} },
        logout: { method: "GET",  params: {action: "logout"} }
    });
    
    // Set login status
    this.perform_login = function (data, user_name) {
		priv_logginUser = user_name;
		$cookieStore.put("auth_user_info", priv_logginUser);
    };
	
	this.login = function (user_name, password, success, fail) {
        var loginsvc = new LoginService();
        loginsvc.user_name = user_name;
        loginsvc.password = password;
        
        loginsvc.$login(
            function (data) {
				self.perform_login(data, user_name);
				if (success) {
					success();
				}
            },
            function (error) {
                // Report Error
                if (fail) {
                    fail(error);
                }
            }
        );
	};
	
	this.logout = function () {
		priv_logginUser = "";
		$cookieStore.remove("auth_user_info");
	};
	
	this.get_username = function () {
		if ( priv_logginUser ) {
			return priv_logginUser;
		} else {
			priv_logginUser = $cookieStore.get("auth_user_info");
			if ( priv_logginUser ) {
				return priv_logginUser;
			}
		}
	};
	
});
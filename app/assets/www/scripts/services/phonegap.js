// Simple value service.
angular.module('PhoneGap.services', [])
// Provide basic navigation
.service('nav', function ($location, $window, $rootScope, $log) {
	/**
	 * This is a very quick and dirty navigation code and highly unreliable because it
	 * does not detect any error condition.  The primary objective is to exit the app
	 * when hitting back from home, `nav_history` is only used as a form of counter
	 * to know when the back button should exit the app instead of going back using
	 * window.history.
	 * 
	 * The implementation need to improve in 2 fronts:
	 * 1. Ensure that history is only added and removed upon successful route chnage
	 * 2. Ensure that goToPage only goes to a valid page
	 * 
	 * Sample implementation can be found at:
	 * - https://github.com/ajoslin/angular-mobile-nav.git
	 */
	var self = this,
		nav_history = [];

	document.addEventListener("deviceready", function() {
		document.addEventListener("backbutton", function() {
			self.goBack();
			if (!$rootScope.$$phase) {
				$rootScope.$apply();
			}
		});
	});

	this.goHome = function () {
		$location.path("/");
		nav_history = [];		
	};

	this.goIntroHome = function () {
		$location.path("/intro");
		nav_history = ["intro"];	
	};
	
	this.goBack = function () {
		if ( nav_history.length === 1 && nav_history[0] === "intro" ) {
			this.goHome();
		} else if ((nav_history.length) > 0) {
			var previous = nav_history.pop();
			$window.history.back();
		} else {
			$log.log("exitApp called.");
			navigator.app.exitApp();
		}
	};
	
	this.goToPage = function (path) {
		$location.path(path);
		nav_history.push(path);
	};
	
	// Similar to goToPage except no history is recorded
	this.navigateTo = function (path) {
		$location.path(path);
	};
})
/*
.factory('nav', function ($navigate) {
	return {
		goHome: function () {
			$navigate.go("/");
			$navigate.eraseHistory();
		},
		goBack: function () {
			$navigate.back();
		},
		goToPage: function (path) {
			$navigate.go(path, true);
		}
	};
})
*/
// phonegap ready service - listens to deviceready
.factory('phonegapReady', function($log) {
	/**
	 * Keep track if device ready flag is set.  If yes, simply run the callback without
	 * skipping the deviceready listening.
	 * 
	 * Optionally passing the $scope to call $apply() if not already in a $digest cycle.
	 */
	'use strict';
	var deviceIsReady = false;
	
	/*
	return function (callback, scope) {
		document.addEventListener('deviceready', callback, false);
		$log.log("phonegapReady: deviceready event used.");
		if ( scope && !scope.$$phase ) {
			scope.$apply();
		}
	};
	*/
	
	return function (callback, scope) {
		var readyCallback = function () {
			deviceIsReady = true;
			callback();
			if ( scope && !scope.$$phase ) {
				scope.$apply();
			}
		};
		if (deviceIsReady) {
			callback();
			$log.log("phonegapReady: deviceIsReady used: ", deviceIsReady);
		} else {
			document.addEventListener('deviceready', readyCallback, false);
			$log.log("phonegapReady: deviceready event used.");
		}
	};
})
.service('geolocation', function (phonegapReady, $log) {
	// Watch for locatin change every 5 seconds
	var self=this,
		readyFlag,
		geoWatchID = null,
		geoOptions = { enableHighAccuracy:true, timeout:10000 };

	// Get location info
	this.get = function (onLocationRefresh, onLocationRefreshError) {
		phonegapReady( function () {
			navigator.geolocation.getCurrentPosition(onLocationRefresh, onLocationRefreshError, geoOptions);
		});
	};
	
	// Stop watch
	this.stopWatch = function () {
		if (geoWatchID) {
			navigator.geolocation.clearWatch(geoWatchID);
			$log.log("GeoWatch ID " + geoWatchID + " cleared.");
			geoWatchID = null;
		}
	};
	
	// Start watch
	this.startWatch = function (onLocationRefresh, onLocationRefreshError) {
		phonegapReady( function () {
			// first call to start
			self.get(onLocationRefresh, onLocationRefreshError);
			// Stop any previously enabled watch
			self.stopWatch();
			// Fire the callback upon init
			//onLocationRefresh();
			// Start the watch
			geoWatchID = navigator.geolocation.watchPosition(
				onLocationRefresh,
				onLocationRefreshError,
				geoOptions
			);
			$log.log("Started the GeoWatch with ID: " + geoWatchID);
		});
	};
	
	return this;
})
.factory('accelerometer', function ($rootScope, phonegapReady) {
    return {
        getCurrentAcceleration: phonegapReady(function (onSuccess, onError) {
            navigator.accelerometer.getCurrentAcceleration(function () {
                var that = this,
                    args = arguments;

                if (onSuccess) {
                    $rootScope.$apply(function () {
                        onSuccess.apply(that, args);
                    });
                }
            }, function () {
                var that = this,
                args = arguments;

                if (onError) {
                    $rootScope.$apply(function () {
                        onError.apply(that, args);
                    });
                }
            });
        })
    };
})
.factory('notification', function ($rootScope, phonegapReady) {
    return {
        alert: phonegapReady(function (message, alertCallback, title, buttonName) {
            navigator.notification.alert(message, function () {
                var that = this,
                    args = arguments;

                $rootScope.$apply(function () {
                    alertCallback.apply(that, args);
                });
            }, title, buttonName);
        }),
        confirm: phonegapReady(function (message, confirmCallback, title, buttonLabels) {
            navigator.notification.confirm(message, function () {
                var that = this,
                    args = arguments;

                $rootScope.$apply(function () {
                    confirmCallback.apply(that, args);
                });
            }, title, buttonLabels);
        }),
        beep: function (times) {
            navigator.notification.beep(times);
        },
        vibrate: function (milliseconds) {
            navigator.notification.vibrate(milliseconds);
        }
    };
})
.factory('navSvc', function($navigate) {
    return {
        slidePage: function (path,type) {
            $navigate.go(path,type);
        },
        back: function () {
            $navigate.back();
        }
    };
})
.factory('compass', function ($rootScope, phonegapReady) {
    return {
        getCurrentHeading: phonegapReady(function (onSuccess, onError) {
            navigator.compass.getCurrentHeading(function () {
                var that = this,
                    args = arguments;

                if (onSuccess) {
                    $rootScope.$apply(function () {
                        onSuccess.apply(that, args);
                    });
                }
            }, function () {
                var that = this,
                    args = arguments;

                if (onError) {
                    $rootScope.$apply(function () {
                        onError.apply(that, args);
                    });
                }
            });
        })
    };
})
.factory('contacts', function ($rootScope, phonegapReady) {
    return {
        findContacts: phonegapReady(function (onSuccess, onError) {
            var options = new ContactFindOptions();
            options.filter="";
            options.multiple=true;
            var fields = ["displayName", "name"];
            navigator.contacts.find(fields, function(r){console.log("Success" +r.length);var that = this,
                args = arguments;
                if (onSuccess) {
                    $rootScope.$apply(function () {
                        onSuccess.apply(that, args);
                    });
                }
            }, function () {
                var that = this,
                    args = arguments;

                if (onError) {
                    $rootScope.$apply(function () {
                        onError.apply(that, args);
                    });
                }
            }, options);
        })
    };
});



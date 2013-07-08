angular.module('Z1kApp')
.controller("IntroCtrl", function ($scope, nav, phonegapReady) {
	$scope.view_animate_prop = { enter: 'example-enter', leave: 'example-leave' };
	$scope.header_name = "Waiting for PhoneGap...";
	$scope.category_name = "Waiting";
	
	// Intentially making 2 different call to phonegapReady to make sure it works.
	phonegapReady( function () { $scope.header_name = "AngGap Ready!!!"; }, $scope);
	phonegapReady( function () { $scope.category_name = "Category"; }, $scope);
	
	$scope.goToPage = nav.goToPage;
	$scope.goToMain = nav.goHome;
})
.controller("IntroGeoCtrl", function ($scope, nav, geolocation, phonegapReady, $log) {
	// Map related
	google.maps.visualRefresh = true;
	var mapOptions = {
			zoom: 16,
			draggable: true,
			mapTypeId: google.maps.MapTypeId.ROADMAP,
			disableDefaultUI: true
		},
		map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions),
		marker;
		
	// Watch for geo location change
	var locationUpdate = function (position) {
			if (position) {
				var pos = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
				map.setCenter(pos);
				if (marker) {
					marker.setPosition(map.getCenter());
				} else {
					marker = new google.maps.Marker({
						position: map.getCenter(),
						map: map
					});
				}
				$log.log("Position: ", pos);
			}
			$scope.loc_status = "Ready...";
			$scope.loc_time = new Date();
			$scope.position=position;

			console.log("Location updated.");
			if (!$scope.$$phase) {
				$scope.$apply();
			}
		},
		locationError = function (error) {
			$scope.loc_status = "Timeout Error.";
			$scope.loc_time = new Date();
			if (!$scope.$$phase) {
				$scope.$apply();
			}
			console.log("Error retrieving position " + error.code + " " + error.message);
		};
		
	$scope.loc_status = "Waiting for location info...";
	geolocation.startWatch(locationUpdate, locationError);
		
	$scope.goHome = function () {
		geolocation.stopWatch();
		nav.goIntroHome();
	};
})
.controller("IntroDBCtrl", function ($scope, nav, phonegapReady, $log) {
	var db,
		errorCB = function (error) {
			$log.log("DB Transaction Error Code " + error.code + ": " + error.message);
		},
		populate_db = function (tx) {
			tx.executeSql("create table if not exists INTRO (id integer primary key autoincrement, name varchar(100), data text)");
			$log.log("Database Initialized.");
		},
		delete_db = function (tx) {
			tx.executeSql("drop table if exists INTRO");
			db.transaction(populate_db, errorCB);
			$log.log("Database content deleted.");
			$scope.rows = [];
			if (!$scope.$$phase) {
				$scope.$apply();
			}
		},
		query_success = function (tx, results) {
			$scope.rows = [];
			var len = results.rows.length;
			for (var i=0; i<len; i+=1) {
				var entry = { "id": results.rows.item(i).id , "name": results.rows.item(i).name, "data": results.rows.item(i).data };
				$scope.rows.push(entry);
			}
			if (!$scope.$$phase) {
				$scope.$apply();
			}
			
			$log.log("QueryDB completed.");
		},
		query_db = function () {
			$log.log("QueryDB called.");
			db.transaction(
				function (tx) {
					tx.executeSql("select * from INTRO", [], query_success, errorCB);
				}
			);
		};
	
	$scope.name = "A Name";
	$scope.data = "Some Data";
	$scope.rows = [];
	
	phonegapReady( function () {
		db = openDatabase("z1k_app", "1.0", "z1k_app Test DB", 1000000);
		db.transaction(populate_db, errorCB);
		query_db();
	});	
	
	$scope.addRow = function () {
		var name = $scope.name,
			data = $scope.data;
		var sql = "insert into INTRO (name, data) values ('" + name + "', '" + data + "')";
		var insertSuccess = function (tx, results) {
			var entry = { "id": results.insertId, "name": name, "data": data };
			$log.log("DB Entry: ", entry);
			$scope.rows.push(entry);
			if (!$scope.$$phase) {
				$scope.$apply();
			}
		};
		db.transaction(
			function (tx) {
				tx.executeSql(sql, [], insertSuccess, errorCB);
			},
			errorCB
		);
	};
	
	$scope.deleteRow = function (id) {
		var sql = "delete from INTRO where id = '" + id + "'",
			deleteSuccess = function (tx, results) {
				for (var i=0; i<$scope.rows.length; i+=1 ) {
					if ( $scope.rows[i].id === id ) {
						$scope.rows.splice(i, 1);
						$log.log("Deleted id: " + id);
						break;
					}
				}
				if (!$scope.$$phase) {
					$log.log("Page refresh: " + id);
					$scope.$apply();
				}
			};
		$log.log("Deleting id: " + id);
		db.transaction( function (tx) {
			tx.executeSql(sql,[], deleteSuccess, errorCB);
		});
	};
	
	$scope.deleteDB = function () {
		db.transaction(delete_db, errorCB);
	};
	
	$scope.goHome = nav.goIntroHome;
	
})
.controller("IntroJSONCtrl", function ($scope, nav, ContactNames, phonegapReady, $timeout, $log) {
	$scope.row_style = {};
	$scope.rows = ContactNames.query();

	// Delete
	$scope.deleteRow = function (contact_id) {
		$scope.status = "";
		var contact = new ContactNames(),
			remove_row_from_rows = function () {
				for (var i=0; i<$scope.rows.length; i+=1 ) {
					if ( $scope.rows[i]._id === contact_id ) {
						$scope.rows.splice(i, 1);
						$log.log("Deleted contact_id: " + contact_id);
						break;
					}
				}
			};
		
		contact.$delete(
			{ contact_id: contact_id },
			function () {
				$scope.row_style[contact_id] = "topcoat-list__item animated fadeOutRight";
				// Allow animation to take place before removing the row
				$timeout(remove_row_from_rows, 800);
			},
			function (error) {
				$scope.status = "Error: " + error.data;
			}
		);
	};
	
	$scope.goHome = nav.goIntroHome;
	$scope.goToPage = nav.goToPage;
})
.controller("IntroJSONDetailCtrl", function ($scope, nav, $log, $route, $routeParams, ContactNames, phonegapReady) {
    // Save or Add Contact
	$scope.contactFormSubmit = function () {
		$scope.status = "";
		if ($scope.editMode) {
			$scope.contact.$save(
				{ contact_id: $routeParams.contact_id },
				function () {
					$scope.status = "Contact Saved.";
				},
				function (error) {
					$scope.status = "Error: " + error.data;
				}
			);
		} else {
			$scope.contact.$add(
				function () {
					$scope.status = "Contact Added.";
				},
				function (error) {
					$scope.status = "Error: " + error.data;
				}
			);
		}
	};

	
    /* --------------------
     * LOAD DATA
     */
    // Configure scope based on form mode
    if ($route.current.form_mode === 'add') {
        $scope.form_title = "New Contact";
        $scope.editMode = false;
        $scope.form_action = "Add";
        $scope.contact = new ContactNames();
        $scope.status = "Ready.";
    } else {
        $scope.form_title = "Contact Edit";
        $scope.editMode = true;
        $scope.form_action = "Save";
        $scope.contact = ContactNames.get(
			{ contact_id: $routeParams.contact_id },
			function () {
				$scope.status = "Ready.";
			},
			function (error) {
				$scope.status = "Error: " + error.data;
			}
        );
        $log.log("Contact: ", $scope.contact);
    }

	$scope.goHome = nav.goIntroHome;
	$scope.goBack = nav.goBack;
    
})
.controller("IntroQRCtrl", function ($scope, nav, $log) {
	$scope.results = ["Awaiting Scan..."];
	
	// Scan
	$scope.scanQR = function () {
		window.plugins.barcodeScanner.scan(
			function(result) {
				$scope.results = [];
				$scope.results.push("Result: " + result.text);
				$scope.results.push("Format: " + result.format);
				$scope.results.push("Cancelled: " + result.cancelled);
				if (!$scope.$$phase) {
					$scope.$apply();
				}
			}, function(error) {
				$scope.results = [ "Scanning failed: " + error ];
				if (!$scope.$$phase) {
					$scope.$apply();
				}
			}
		);
	};

	// Generate
	$scope.generateQR = function () {
		window.plugins.barcodeScanner.encode(
			BarcodeScanner.Encode.TEXT_TYPE, $scope.qr_text,
			function(success) {
				$scope.status = "Enconding completed.";
			},
			function(error) {
				$scope.status = "Enconding failed: " + error;
			}
		);
	};
	
	$scope.goHome = nav.goIntroHome;
})
.controller("IntroAnimCtrl", function ($scope, nav, $timeout, $log) {
	// Angular Animate
	$scope.show_ang = true;

	// Manual Animate
	var show_manual = true;
	$scope.toggleManualAnimate = function () {
		show_manual = !show_manual;
		if (show_manual) {
			$scope.manual_animate = "animated fadeInRight";
		} else {
			$scope.manual_animate = "animated fadeOutRight";
		}
	};

	// Right Big
	var rightbig = true;
	$scope.toggleRightBig = function () {
		if (rightbig) {
			$scope.class_rightbig = "animated fadeOutRightBig";
		} else {
			$scope.class_rightbig = "animated fadeInRightBig";
		}
		rightbig = !rightbig;
	};
	
	// Down Big
	var downbig = true;
	$scope.toggleDownBig = function () {
		if (downbig) {
			$scope.class_downbig = "animated fadeOutDownBig";
		} else {
			$scope.class_downbig = "animated fadeInDownBig";
		}
		downbig = !downbig;
	};
	
	
	// Shake button
	$scope.setShake = function () {
		$scope.class_shake = "animated shake topcoat-button--cta";
		navigator.notification.vibrate(200);
		$timeout(function () {$scope.class_shake="";}, 800);
	};
	
	// Wobble
	$scope.setWobble = function () {
		$scope.class_wobble = "animated wobble topcoat-button--cta";
		$timeout(function () {$scope.class_wobble="";}, 800);
	};

	// Flash
	$scope.setFlash = function () {
		$scope.class_flash = "animated flash topcoat-button--cta";
		$timeout(function () {$scope.class_flash="";}, 800);
	};
	
	$scope.goHome = nav.goIntroHome;
});

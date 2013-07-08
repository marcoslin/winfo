angular.module('Z1kApp', ['ngMobile','PhoneGap.services','introJson.services','Nav.directives'])
.config(function ($routeProvider) {
	// Note: only route defined with require_auth:true will be checked for Authorization
	$routeProvider
		// App Related
		.when('/profile', { templateUrl: 'views/main.html', controller: 'MainCtrl' } )
		.when('/nearby', { templateUrl: 'views/nearby.html', controller: 'MainCtrl' } )
		.when('/livebook', { templateUrl: 'views/livebook.html', controller: 'MainCtrl' } )
		.when('/settings', { templateUrl: 'views/settings.html', controller: 'MainCtrl' } )
		
		// Intro Related
		.when('/intro', { templateUrl: 'intro/views/intro.html', controller: 'IntroCtrl' } )
		.when('/intro/geo', { templateUrl: 'intro/views/intro_geo.html', controller: 'IntroGeoCtrl' } )
		.when('/intro/db', { templateUrl: 'intro/views/intro_db.html', controller: 'IntroDBCtrl' } )
		.when('/intro/contact', { templateUrl: 'intro/views/intro_json.html', controller: 'IntroJSONCtrl' } )
		.when('/intro/contact/add', { templateUrl: 'intro/views/intro_json_detail.html', controller: 'IntroJSONDetailCtrl', form_mode: "add" } )
		.when('/intro/contact/:contact_id', { templateUrl: 'intro/views/intro_json_detail.html', controller: 'IntroJSONDetailCtrl', form_mode: "edit" } )
		.when('/intro/qr', { templateUrl: 'intro/views/intro_qr.html', controller: 'IntroQRCtrl' } )
		.when('/intro/anim', { templateUrl: 'intro/views/intro_anim.html', controller: 'IntroAnimCtrl' } )
		
		.otherwise({ redirectTo: '/profile' });
});

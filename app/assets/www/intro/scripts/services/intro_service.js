angular.module("introJson.services", ['ngResource'])
    .factory('ContactNames', function ($resource) {
		url = "https://z1kserver-dev.appspot.com/intro/contact/:contact_id";
		//url = "http://localhost:8080/intro/contact/:contact_id";
        return $resource(
			url,
			{},
			{
				'query':  {method:'GET', isArray:true},
				'get':    {method:'GET'},
				'save':   {method:'PUT'},
				'add':   {method:'POST'},
				'delete': {method:'DELETE'}
			}
        );
    });

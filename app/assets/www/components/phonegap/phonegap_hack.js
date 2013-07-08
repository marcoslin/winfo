//Major hack to press the dialog box from ripple
if ( document.getElementById('tinyhippos-injected') ) {
	console.log("Ripple Emulator Detected.  Applying Hacks.");
	window._cordovaNative = true;

	var hackReady = function () {
		// Make ripple think that a back button handler has already been attached
		cordova.addDocumentEventHandler('backbutton'); 

		document.addEventListener("backbutton", function(){
			alert("Pressed back");
		});
	};

	document.addEventListener("deviceready", hackReady, true);
}

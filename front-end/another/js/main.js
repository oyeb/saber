$(document).ready(function() {
 
    
    jQuery(window).load(function () {
    	$('body').addClass('loaded');
    	setTimeout(function(){
    		$('#banner').addClass('jello animated');
    		$('#of').addClass('tada animated');
    	},1000);


    	var date = new Date();

    	$("#time").html(date.toString());


    	$('#story').typed({
            strings: [">> ^100 Welcome to Battle Of Bots ^500 <br> ^ You have been warned about the dangers ahead",
    		">> We have been waiting for a hacker like you for more than 20 years"
    	],
            typeSpeed: 20,
            backDelay: 100,
            loop: false,
            loopCount: false,
		});
		$("#typed").typed('reset');
   	});
});
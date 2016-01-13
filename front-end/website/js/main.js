$(document).ready(function() {
 
    
    jQuery(window).load(function () {
    	$('body').addClass('loaded');
    	setTimeout(function(){
    		$('#banner').addClass('jello animated');
    	},1000);
   	});
});
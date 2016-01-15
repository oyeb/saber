$(document).ready(function($) {
 
    
    jQuery(window).load(function () {
    	$('body').addClass('loaded');
    	setTimeout(function(){
    		$('#banner').addClass('jello animated');
    	},1000);


    	var nt_example2 = $('#bob').newsTicker({
	row_height: 60,
	max_rows: 1,
	speed: 300,
	duration: 6000,
	prevButton: $('#bob-prev'),
	nextButton: $('#bob-next'),
	hasMoved: function() {
    	$('#bob-infos-container').fadeOut(200, function(){
        	$('#bob-infos .infos-hour').text($('#bob li:first span').text());
        	$('#bob-infos .infos-text').text($('#bob li:first').data('infos'));
        	$(this).fadeIn(400);
        });
    },
    pause: function() {
    	$('#bob li i').removeClass('fa-play').addClass('fa-pause');
    },
    unpause: function() {
    	$('#bob li i').removeClass('fa-pause').addClass('fa-play');
    }
});
$('#bob-infos').hover(function() {
    nt_example2.newsTicker('pause');
}, function() {
    nt_example2.newsTicker('unpause');
});

   	});

});
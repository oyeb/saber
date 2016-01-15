$(document).ready(function() {
 
    
    jQuery(window).load(function () {

    	var date = new Date();

    	$("#time").html(date.toString());

    	var command = [">>"];

		var type = function () {
			$('#story').typed({
		                strings: command,
		                typeSpeed: 5,
		                backDelay: 500,
		                loop: false,
		                loopCount: false,
			});

			return ;
		}

		$('#command').submit(function (request) {

			$("#story").typed('reset');
			
			if($('#input').val() == "menu"){
				command = [">> Enter the respective page you want to visit: ^300<br> Home<br> ^300 Details<br> ^300 Submissions<br> ^300 Leaderboard<br> ^300 Contact Us<br>>>"];
				type();
				
			}else if($('#input').val() == "clear"){
				command = [">>"];
				type();
			}else if($('#input').val() == "help"){
				command = ["Brolog has nothing to do with Prolog, the language of AI.^10<br>bob is not an AI,^300 but it understands Brolog.^50<br>You must learn Brolog.<br>Try `learn`<br>>>"];
				type();
			}else{
				command = [">> Enter a valid command<br>>>"];
				type();
			}
			request.preventDefault();
			return false;
		});
	});
});
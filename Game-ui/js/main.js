$(document).ready(function(){

	var canvas = $('#game').get(0);

	if(canvas.getContext){

		var game = canvas.getContext('2d');

		var img = new Image();

		img.width = 20;

		img.height = 20;

		game.imageSmoothingEnabled = true;

		img.src = 'img/server.png';

		console.log(img);

		img.onload = function () {
			game.drawImage(img,60,60,10,10);

			game.drawImage(img,300,300,30,30);
		}

		
 
	}


});
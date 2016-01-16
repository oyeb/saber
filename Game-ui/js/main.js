$(document).ready(function(){

	var canvas = $('#game').get(0);

	canvas.width = window.innerWidth;
	canvas.height = window.innerHeight;

	b = canvas.width;

	l = canvas.height;

	var gameState = {

		no_of_bots : 2,

		colors : ["red","blue","yellow","green"],

		bots : [
			[{

				x : 10,	

				y : 10,

				signals : [{

					bot_type : 1,

					bot_no : 1,

				}]	,			

			},

			{

				x : 20,	

				y : 40,

			},

			{

				x : 30,	

				y : 80,

			}],

			[{

				x : 90,	

				y : 90,


			},

			{

				x : 50,	

				y : 40,

			},

			{

				x : 60,	

				y : 70,

			}]

		],

		scores : [100,200], 


	};

	var signals  = [];


	if(canvas.getContext){

		var game = canvas.getContext('2d');

		/*

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

		*/
	
		// Creating a signal
		
		function drawBots(){

			var i = 0;

			gameState.bots.forEach(function (bots) {

				
				bots.forEach(function (bot) {
					
					game.beginPath();
				
					game.strokeStyle = gameState.colors[i];

					game.arc((bot.x*canvas.width)/100,(bot.y*canvas.height)/100,10,0,Math.PI*2,true);

					game.stroke();


				});

				i++;

			});

		}

		function drawScore () {

			var i = 0;

			game.font = "20px serif";

			game.fillStyle = "white";

			game.fillText("Scores", (90*canvas.width)/100, (10*canvas.height)/100);
			
			gameState.scores.forEach(function (score) {

				game.fillStyle = gameState.colors[i];
					
				game.fillText("Bot "+ i.toString() + ":" + score.toString(), (90*canvas.width)/100, (((10+((i+1)*5))*canvas.height)/100));

				console.log(score);

				i++;	

			});

		}

		var i = 0;

		function drawSignals () {
			
			gameState.bots.forEach(function (bots) {
				
				bots.forEach(function (bot) {

					if(bot.signals){
					
						bot.signals.forEach(function(signal){

							game.strokeStyle = "white";

							game.beginPath();

							var to = gameState.bots[signal.bot_type][signal.bot_no];

							var distance_x = Math.abs(((bot.x*b)/100)-((to.x*b)/100));

							var distance_y = Math.abs(((bot.y*l)/100)-((to.y*l)/100));

							game.moveTo((bot.x*b)/100,(bot.y*l)/100);

							game.lineTo(((bot.x*b)/100)+(distance_x*i),((bot.y*l)/100)+(distance_y*i));

							game.stroke();


						});

					}

				});

			});

			if( i < 1 ){

				i += 0.01;

			}

		}

		function drawMap(){

			game.clearRect(0, 0, canvas.width, canvas.height);

			drawBots();

			drawScore();

			drawSignals();


		}


		if(typeof game_loop != "undefined") clearInterval(game_loop);
		game_loop = setInterval(drawMap, 60);
 
	}


});
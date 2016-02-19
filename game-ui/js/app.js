
// A cross-browser requestAnimationFrame
// See https://hacks.mozilla.org/2011/08/animating-with-javascript-from-setinterval-to-requestanimationframe/

/**
 *
 *  To call main function regularly 
 *
 */
var requestAnimFrame = (function(){
    return window.requestAnimationFrame ||
        function(callback){
            window.setTimeout(callback, 1000 / 60);
        }
})();

// Create the canvas
var canvas = document.createElement("canvas");
var ctx = canvas.getContext("2d");
canvas.width = 800;//setting width
canvas.height = 450;//setting height
document.body.appendChild(canvas);

// The main game loop
var lastTime;
var turn=0;
function main() {
    var now = Date.now();
    var dt = (now - lastTime) / 1000.0;
    console.log(dt);
    if(dt%180 == 0 ){
        turn++;
    }

    if(turn >= gameState.turns.length){
        gameOver();
    }else{
        update(dt);
        render();

        lastTime = now;
        requestAnimFrame(main);
    }
};

function init() {
    terrainPattern = ctx.createPattern(resources.get('img/terrain.png'), 'repeat');

    document.getElementById('play-again').addEventListener('click', function() {
      //  reset();
    });

    //reset();
    lastTime = Date.now();
    start();
    main();
}

resources.load([
    'img/sprites.png',
    'img/terrain.png',
    'img/server0.png'
]);
resources.onReady(init);


var lastFire = Date.now();
var gameTime = 0;
var isGameOver;
var terrainPattern;

var score = 0;
var scoreEl = document.getElementById('score');

var gameState = {
    init : {

        width : 800,
        aspect : 1.7,
        turntime : 2,
        lt : 2,
        bot_count : 2,
        server_count : 2,
        bot_data : [
            {
                x : 0.25,
                y : 0.4,
                res_health : 15,
                invested : 0,
                max : 80,
                type : 0,
                id : 1
            },
            {
                x : 0.75,
                y : 0.4,
                res_health : 40,
                invested : 0,
                max : 80,
                type : 1,
                id : 2
            },
            {
                x : 0.5,
                y : 0.8,
                res_health : 15,
                invested : 0,
                max : 60,
                type : -1,
                id:3
            }
        ]

    },
    turns : [
        [
            {
                attacker : 1 ,
                victim : 3,
                arate : 40,
                state : 'attacking',
                length : 40,
                full_distance : 100

            }
        ]
    ]
}

var bots = gameState.bot_data;


// Speed in pixels per second
// 
var signalSpeed = 50;
var retractSignalSpeed = 100;

// Update game objects
function update(dt) {
    gameTime += dt;

    //handleInput(dt);
    updateEntities(dt);
    

    scoreEl.innerHTML = score;
};

function start(){
    gameState.init.bot_data.forEach(function(bot) {
        var count = gameState.init.server_count;
        while(count >= -1){
            if(bot.type == count){
                bot.sprite =`img/server{{count+1}}.png`;
            }
        }
        bot.signals = [];
        bots.push(bot);
    });
}

function updateEntities(dt) {
    // Update the player sprite animation
    //player.sprite.update(dt);

    gameState.init.turns[turn].forEach(function(signals) {
        signals.init.forEach(function(signal){
            var attacker = signal.attacker;
            for (var i = 0; i < bots[attacker].signal.length; i++) {
                if(bots[attacker].signal[i].victim === signal.victim){
                    bots[attacker].signal[i] = signal;
                    found = true;
                }
            };
            if(found === false){
                var s = signal;
                signal.sprite =`img/signal{{bots[attacker].type+1}}.png`;
                bots[attacker].signals.push(signals);
            }
        });
    });



    /*
    gameState.bots_data[turn].forEach(function(bot) {
        bots[bot.id].res_health = bot.res_health;
        bots[bot.id].invested = bot.invested;
    });
    */
}

// Draw everything
function render() {
    ctx.fillStyle = terrainPattern;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    renderSignals();
    renderBots();
};
/*
function renderEntities(list) {
    for(var i=0; i<list.length; i++) {
        renderEntity(list[i]);
    }    
}
*/

function renderSignals() {
    bots.forEach(function(bot){
        bot.signals.forEach(function(signal){
            renderSignal(bot,signal);
        });
    });
}

function renderSignal(bot,signal){
    var both_ways = 0;
    var signal_no = 0;
    for (var i = 0; i < bots[signal.victim].signals.length-1; i++) {
        if(bots[bot.victim].signals[i].victim == signal.attacker){
            both_ways = 1;
            signal_no = i;
        }
    };
    if(both_ways == 1){
        if(signal.length > (signal.full_distance/2)){
            signal.length -= 36;
        }
    }
    var v_x = bots[signal.victim].x;
    var v_y = bots[signal.victim].y;
    var p = signal.length/signal.total;
    var des_x = bot.x + p(v_x-bot.x);
    var des_y = bot.y + p(v_y-bot.y);
    ctx.setLineDash([5, 15]);

    ctx.beginPath();
    ctx.moveTo(bot.x,bot.y);
    ctx.lineTo(des_x, des_y);
    ctx.stroke();
}

function renderBots(){
    gameState.init.bot_data.forEach(function(bot){
        //draw Bot
    });
}


// Game over
function gameOver() {
    document.getElementById('game-over').style.display = 'block';
    document.getElementById('game-over-overlay').style.display = 'block';
    isGameOver = true;
}

/*
// Reset game to original state
function reset() {
    document.getElementById('game-over').style.display = 'none';
    document.getElementById('game-over-overlay').style.display = 'none';
    isGameOver = false;
    gameTime = 0;
    score = 0;

};

*/
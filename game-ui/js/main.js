// requestAnimationFrame() shim by Paul Irish
// http://paulirish.com/2011/requestanimationframe-for-smart-animating/
window.requestAnimFrame = (function() {
    return window.requestAnimationFrame ||
        window.webkitRequestAnimationFrame ||
        window.mozRequestAnimationFrame ||
        window.oRequestAnimationFrame ||
        window.msRequestAnimationFrame ||
        function( /* function */ callback, /* DOMElement */ element) {
            window.setTimeout(callback, 1000 / 60);
        };
})();

// Create the canvas    
var canvas = $('#game')[0];
var context = canvas.getContext("2d");
canvas.height = window.innerHeight;
canvas.width = canvas.height * 1.77; //setting width
console.log(canvas.width);
width = canvas.width;
height = canvas.height;
var startState;
var serverImages = [];
var lastTime;
var servers;
var colors = ['Black', 'Red', 'Blue', 'Green', 'Pink'];
var pattern;
var imageObj;
var server_status;
var count = 0;
var turntime = 1;
var turn = 0;
var animate;
var next_connections;
var current_connections;
var current_servers;
var next_servers;
var turn_no = 1;
var input_stream = [];
var val_stream = [];
var ign_stream = [];
var inv_stream = [];
var notifications = [];
var unpause = true;
var team_id;

function drawBG() {
    context.rect(0, 0, canvas.width, canvas.height);
    context.fillStyle = pattern;
    context.fill();
}

function drawDebug() {

    var debug = $('.debug');
    
    
    for (var i = 0;input_stream.length > 0 &&  i < input_stream[turn_no].length; i++) {   
    debug.html('');
    var data = ""; 
        var str = input_stream[turn_no][i].split('\n');
        data += "<div>";
        for (var j = 0; j < str.length; j++) {
            data += "<p>" + str[j] + "</p>";
        }
        data += "</div>";
        debug.append(data);
    }


    var stream = $('#stream');
    stream.html('   ');
    var data = "<div>";
    data += "<p>Turn No : " + turn_no + "</p>";
    for (var i = 0; val_stream.length > 0 && i < val_stream[turn_no].length; i++) {

        data += "<p class='val'>" + val_stream[turn_no][i] + "</p>";
    }
    for (var i = 0; ign_stream.length > 0 && i < ign_stream[turn_no].length; i++) {

        data += "<p class='ign'>" + ign_stream[turn_no][i] + "</p>";
    }
    for (var i = 0; inv_stream.length > 0 && i < inv_stream[turn_no].length; i++) {

        data += "<p class='inv'>" + inv_stream[turn_no][i] + "</p>";
    }
    data += "</div>";
    stream.append(data);


        var notify = $('.notification');
    var data_n = "";
    notify.html('');
    data_n += "<p>Turn No : " + turn_no + "</p>";
    for (var i = 0; i < notifications[turn_no].length; i++) {
        data_n += "<div>";
        if (notifications[turn_no][i].type == 'p') {
            data_n += "<p>Action Occurred: Server Lost</p>";
        } else if (notifications[turn_no][i].type == 'w') {
            data_n += "<p>Action Occurred: Auto-Withdraw</p>";
        } else if (notifications[turn_no][i].type == 'i') {
            data_n += "<p>Action Occurred: Insufficient Resources</p>";
        }
        data_n += "<p>Time(elapsed after last turn) : " + notifications[turn_no][i].epoch + "</p>";
        data_n += "<p>Message : " + notifications[turn_no][i].msg + "</p>";
        data_n += "<p>Bot Id : " + notifications[turn_no][i].bot_id + "</p>";
        data_n += "</div><hr>";
    }
    notify.append(data_n);
}

function drawServers() {
    //Have to check from the GAME_REPLAY. Currently just getting it from the game start
    for (var i = 0; i < GAME_START.servers.length; i++) {
        var x = (GAME_START.servers[i].pos[0]) * width;
        var y = GAME_START.servers[i].pos[1] * height;
        var imgOBJ;
        switch (GAME_REPLAY[turn].servers[i].owner) {
            case 0:
                imgOBJ = serverImages[0];
                break;
            case 1:
                imgOBJ = serverImages[1];
                break;
            case 2:
                imgOBJ = serverImages[2];
                break;
            case 3:
                imgOBJ = serverImages[3];
                break;
            default:
                imgOBJ = serverImages[4];
                break;
        }
        context.drawImage(imgOBJ, x, y)
    }
}

function drawHealth() {
    for (var i = 0; i < GAME_START.servers.length; i++) {
        var x = ((GAME_START.servers[i].pos[0]) * width) + 8;
        var y = (GAME_START.servers[i].pos[1] * height) + 36;
        switch (GAME_REPLAY[turn].servers[i].owner) {
            case 0:
                context.fillStyle = colors[0];
                break;
            case 1:
                context.fillStyle = colors[1];
                break;
            case 2:
                context.fillStyle = colors[2];
                break;
            case 3:
                imgOBJ = serverImages[3];
                break;
            default:
                context.fillStyle = colors[4];
                break;
        }
        context.font = '8pt Calibri';

        context.fillText(Math.floor(servers[i].reserve), x, y);
    }
}

function drawSignals() {
    for (var i = 0; i < connections.length; i++) {
        var con = connections[i];
        if (con.state <= 3) {
            var ratio = con.length / con.fdist;
            var dis_x = GAME_START.servers[con.sink].pos[0] - GAME_START.servers[con.src].pos[0];
            var dis_y = GAME_START.servers[con.sink].pos[1] - GAME_START.servers[con.src].pos[1];
            var point_x = (GAME_START.servers[con.src].pos[0] + ratio * (dis_x)) * width;
            var point_y = (GAME_START.servers[con.src].pos[1] + ratio * (dis_y)) * height;
            context.beginPath();
            context.setLineDash([1, 2]);
            var color = GAME_REPLAY[turn].servers[con.src].owner;
            switch (color) {
                case 0:
                    context.strokeStyle = colors[0];
                    break;
                case 1:
                    context.strokeStyle = colors[1];
                    break;
                case 2:
                    context.strokeStyle = colors[2];
                    break;
                case 3:
                    context.strokeStyle = colors[3];
                    break;
                default:
                    context.strokeStyle = colors[4];
                    break;
            }

            context.moveTo((GAME_START.servers[con.src].pos[0] * width) + 12, (GAME_START.servers[con.src].pos[1] * height) + 12);
            context.lineTo(point_x + 12, point_y + 12);
            context.stroke();
        } else {
            var ratio = con.length / con.fdist;
            var dis_x = GAME_START.servers[con.src].pos[0] - GAME_START.servers[con.sink].pos[0];
            var dis_y = GAME_START.servers[con.src].pos[1] - GAME_START.servers[con.sink].pos[1];
            var point_x = (GAME_START.servers[con.sink].pos[0] + ratio * (dis_x)) * width;
            var point_y = (GAME_START.servers[con.sink].pos[1] + ratio * (dis_y)) * height;
            context.beginPath();
            context.setLineDash([1, 2]);
            var color = GAME_REPLAY[turn].servers[con.src].owner;
            switch (color) {
                case 0:
                    context.strokeStyle = colors[0];
                    break;
                case 1:
                    context.strokeStyle = colors[1];
                    break;
                case 2:
                    context.strokeStyle = colors[2];
                    break;
                case 3:
                    context.strokeStyle = colors[3];
                    break;
                default:
                    context.strokeStyle = colors[4];
                    break;
            }
            context.moveTo((GAME_START.servers[con.sink].pos[0] * width) + 12, (GAME_START.servers[con.sink].pos[1] * height) + 12);
            context.lineTo(point_x + 12, point_y + 12);
            context.stroke();
        }
    }
}

function render(turn) {
    drawBG();
    drawServers();
    drawHealth();
    drawSignals();
    drawDebug();
    console.log()
}


function preprocess() {

    for (var i = 0; MYBOT_IP_STREAM.length > 0 && i < MYBOT_IP_STREAM.length;) {
        var turn = MYBOT_IP_STREAM[i].split('\n')[0].split('~')[1];
        input_stream[turn] = [];
        var temp = MYBOT_IP_STREAM[i].split('\n')[0].split('~')[1];
        while (temp == turn && i < MYBOT_IP_STREAM.length) {
            var str = MYBOT_IP_STREAM[i];
            input_stream[turn].push(str);
            i++;
            if (i < MYBOT_IP_STREAM.length)
                temp = MYBOT_IP_STREAM[i].split('\n')[0].split('~')[1];
        }
    }
    for (var i = 0, j = 0; MYBOT_VAL_STREAM.length > 0 && i <= GAME_REPLAY[GAME_REPLAY.length - 1].turn;) {
        var turn = MYBOT_VAL_STREAM[j].turn;
        while (i != turn) {
            val_stream[i] = [];
            i++;
        }
        val_stream[i] = [];
        while (turn == i && j < MYBOT_VAL_STREAM.length) {
            for (var k = 0; k < MYBOT_VAL_STREAM[j].moves.length; k++) {
            val_stream[i].push(MYBOT_VAL_STREAM[j].moves[k]);
        }
            j++;
            if (j < MYBOT_VAL_STREAM.length)
                turn = MYBOT_VAL_STREAM[j].turn;
        }
        i++;
        if (j < MYBOT_VAL_STREAM.length) {
            continue;
        } else {
            while (i <= GAME_REPLAY[GAME_REPLAY.length - 1].turn) {
                val_stream[i] = [];
                i++;
            }
        }
    }

    for (var i = 0, j = 0; MYBOT_IGN_STREAM.length > 0 && i <= GAME_REPLAY[GAME_REPLAY.length - 1].turn;) {
        var turn = MYBOT_IGN_STREAM[j].turn;
        while (i != turn) {
            ign_stream[i] = [];
            i++;
        }
        ign_stream[i] = [];
        while (turn == i && j < MYBOT_IGN_STREAM.length) {
            for (var k = 0; k < MYBOT_IGN_STREAM[j].moves.length; k++) {
            ign_stream[i].push(MYBOT_IGN_STREAM[j].moves[k]);
        }
            j++;
            if (j < MYBOT_IGN_STREAM.length)
                turn = MYBOT_IGN_STREAM[j].turn;
        }
        i++;
        if (j < MYBOT_IGN_STREAM.length) {
            continue;
        } else {
            while (i <= GAME_REPLAY[GAME_REPLAY.length - 1].turn) {
                ign_stream[i] = [];
                i++;
            }
        }
    }

    for (var i = 0, j = 0; MYBOT_INV_STREAM.length > 0 && i <= GAME_REPLAY[GAME_REPLAY.length - 1].turn;) {
        var turn = MYBOT_INV_STREAM[j].turn;
        while (i != turn) {
            inv_stream[i] = [];
            i++;
        }
        inv_stream[i] = [];
        while (turn == i && j < MYBOT_INV_STREAM.length) {
            for (var k = 0; k < MYBOT_INV_STREAM[j].moves.length; k++) {
            inv_stream[i].push(MYBOT_INV_STREAM[j].moves[k]);
        }
            j++;
            if (j < MYBOT_INV_STREAM.length)
                turn = MYBOT_INV_STREAM[j].turn;
        }
        i++;
        if (j < MYBOT_INV_STREAM.length) {
            continue;
        } else {
            while (i <= GAME_REPLAY[GAME_REPLAY.length - 1].turn) {
                inv_stream[i] = [];
                i++;
            }
        }
    }

    for (var i = 0, j = 0;GAME_NOTIFICATIONS.length > 0 &&  i <= GAME_REPLAY[GAME_REPLAY.length - 1].turn;) {
        var turn = GAME_NOTIFICATIONS[j].turn;
        while (i != turn) {
            notifications[i] = [];
            i++;
        }
        notifications[i] = [];
        while (turn == i && j < GAME_NOTIFICATIONS.length) {
            notifications[i].push(GAME_NOTIFICATIONS[j]);
            j++;
            if (j < GAME_NOTIFICATIONS.length)
                turn = GAME_NOTIFICATIONS[j].turn;
        }
        i++;
        if (j < GAME_NOTIFICATIONS.length) {
            continue;
        } else {
            while (i <= GAME_REPLAY[GAME_REPLAY.length - 1].turn) {
                notifications[i] = [];
                i++;
            }
        }
    }

}

function main() {


    if (unpause) {
        var current = Date.now();
        var dt = (current - lastTime) / 1000.0;
        lastTime = current;
        if ((count % turntime == 0) && turn < GAME_REPLAY.length - 1) {
            turn++;
            animate = 0;
            current_servers = get_servers_status(turn);
            servers_status = GAME_REPLAY[turn].alive;
            current_connections = get_connections(turn);
            connections = current_connections;
            servers = current_servers;
        }
        /*
        else{
            for(var i=0;i<next_connections.length;i++){
                connections[i].length = current_connections[i].length + (dt)*(next_connections[i].length -current_connections[i].length);
            }
            for(var i=0;i<servers.length;i++){
                servers[i].reserve +=  dt*(next_servers[i].reserve - servers[i].reserve);
            }
            animate  = ((count%turntime)/turntime);
            if(animate > 1){
                animate = 1;
            }
        }*/
        if (turn < GAME_REPLAY.length - 1) {
            count++;
            turn_no = GAME_REPLAY[turn].turn;
            render(turn);
            requestAnimFrame(main);
        } else {
            /*$('#display_score').show( "slow", function() {
            var score = "";
            for(var i=0;i<GAME_START.bot_count;i++){
                score += "<p>Bot "+ (i+1) + ":"+ GAME_END.scores[i] +"</p>";
            }
            $('#score').html(score);
        });
        */
        }
    } else {
        turn_no = GAME_REPLAY[turn].turn;
        current_servers = get_servers_status(turn);
        servers_status = GAME_REPLAY[turn].alive;
        current_connections = get_connections(turn);
        connections = current_connections;
        servers = current_servers;
        render(turn);
        requestAnimFrame(main);
    }


}


function init() {

    imageObj = new Image();
    imageObj.onload = function() {
        pattern = context.createPattern(imageObj, 'repeat');

        context.rect(0, 0, canvas.width, canvas.height);
        context.fillStyle = pattern;
        context.fill();
    };
    imageObj.src = 'img/terrain.png';


    for (var i = 0; i < 5; i++) {
        serverImages.push(new Image());
        serverImages[serverImages.length - 1].src = "img/server" + i + ".png";
    };

    for (var i = -1; i < GAME_START.bot_count; i++) {
        console.log(i);
        var color = "";
        switch (i) {
            case 0:
                color = colors[0];
                break;
            case 1:
                color = colors[1];
                break;
            case 2:
                color = colors[2];
                break;
            case 3:
                color = colors[3];
                break;
            default:
                color = colors[4];
                break;
        }
        console.log("<tr><td class='tg-g145'>" + i + "</td><td class='tg-dgof'>" + color + "</td></tr>");
        $('.tg').append("<tr><td class='tg-g145'>" + i + "</td><td class='tg-dgof'>" + color + "</td></tr>");
    }

    lastTime = Date.now();
    preprocess();
    main();
}


$('#pause').on('click', function(event) {
    unpause = false;
});
$('#prev').on('click', function(event) {
    if (turn - 30 > 0)
        turn -= 30;
    //unpause  = false;
});
$('#next').on('click', function(event) {
    if (turn + 10 < GAME_REPLAY.length)
        turn += 10;
    //unpause  = false;
});
$('#continue').on('click', function(event) {
    unpause = true;
});
$('#speed_up').on('click', function(event) {
    if (turntime - 5 >= 0)
        turntime -= 5;
});
$('#speed_down').on('click', function(event) {
    if (turntime + 5 <= 2000)
        turntime += 5;
});
init();

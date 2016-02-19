/*
Connection Object{
	fdist: 20.180436070610565,
	arate: 0.4,
	status: 1,
	src: 1,
	sink: 2,
	length: 20.180436070610565
}
*/
function get_connections(turn_no){
	var turn_data = GAME_REPLAY[turn_no];
	var active_conns=[];
	for(var i=0;i< turn_data.servers.length;i++){
		conns = turn_data.servers[i].connections;
		for(var j=0; j < conns.length; j++){
			active_conns.push(conns[j]);
		}
	}
	// list of conn objects
	return active_conns;
}

function get_servers_status(turn_no){
	var turn_data = GAME_REPLAY[turn_no];
	var server_statuses=[];
	for(var i = 0; i < turn_data.servers.length; i++){
		server_statuses.push(
			{
			'reserve'  : turn_data.servers[i].reserve,
			'invested' : turn_data.servers[i].invested,
			'owner'    : turn_data.servers[i].owner}
		);
	}
	//list of server* objects
	return server_statuses;
}

function get_init(){
	var init_data = {
		width        : 800,
        aspect       : GAME_START.aspect,
        turntime     : 2,
        lt           : 2,
        bot_count    : GAME_START.bot_count,
        server_count : GAME_START.servers.length,
        clusters     : GAME_START.clusters,
        bot_data     : []
    };
    for (var i=0; i<GAME_START.servers.length; i++){
    	init_data.bot_data.push({
    		x        : GAME_START.servers[i].pos[0],
    		y        : GAME_START.servers[i].pos[1],
    		reserve  : GAME_START.servers[i].reserve,
    		invested : GAME_START.servers[i].invested,
    		max      : GAME_START.servers[i].limit,
    		type     : GAME_START.servers[i].owner,
    	});
    }
    return init_data;
}
/*
 * DON'T EDIT THIS FILE
 * This contains the Server and Connection Object definitions, provided to your bot through the
 * interface `Quantum.h`
 *
*/

#include "util.h"

int state_map(string state_str){
	map<string,int> STATE_MAP;

	STATE_MAP["making"]      = 0;
	STATE_MAP["connected"]   = 1;
	STATE_MAP["withdrawing"] = 2;
	STATE_MAP["headon"]      = 3;
	STATE_MAP["whostile"]    = 4;
	return STATE_MAP[state_str];
}

string inv_state_map(int state_index){
	map<int,string> INV_ST_MAP;

	INV_ST_MAP[0] = "making";
	INV_ST_MAP[1] = "connected";
	INV_ST_MAP[2] = "withdrawing";
	INV_ST_MAP[3] = "headon";
	INV_ST_MAP[4] = "whostile";
	return INV_ST_MAP[state_index];
}

// CONNETION OBJECT
// ---------------------------------------------------------------------------
Connection::Connection(	int _attacker,
						int _victim,
						float _arate,
						float _distance,
						int _state=0){
	attacker = _attacker;
	victim = _victim;
	arate = _arate;
	state = _state;
	length = 0;
	full_distance = _distance;
}

void Connection::sync(	float _arate,
						int _state,
						float _length){
	arate = _arate;
	state = _state;
	length = _length;
}

int Connection::get_attacker(){
	return attacker;
}

int Connection::get_victim(){
	return victim;
}

int Connection::get_state(){
	return state;
}

float Connection::get_full_distance(){
	return full_distance;
}

float Connection::get_length(){
	return length;
}

string Connection::show(){
	string res;
    res = "A:"+to_string(attacker)+" V:"+to_string(victim)+" {fdist:"+to_string(full_distance)+",state:"+to_string(state)+",length:"+to_string(length)+",arate:"+to_string(arate)+"}";
    return res;
}

// SERVER OBJECT
// ---------------------------------------------------------------------------
Server::Server(	pair<float,float> _pos,
				float _power,
				float _maxpow,
				int _owner,
				int _index){
	pos = _pos;
	reserve = _power;
	invested = 0;
	owner = _owner;
	index = _index;
	limit = _maxpow;
}
/*
float update_pow(float dr,float di){
	if((reserve < limit) || dr < 0){
		reserve += dr;
	}else{
		reserve = limit;
	}
	invested += di;
	return reserve;
}
*/
void Server::sync(float _reserve,float _invested,float _owner){
	//sync object data with the game engine's copy
	reserve = _reserve;
	invested = _invested;
	owner = _owner;
}

bool Server::connection_exists(int v_sid, int _state){
	for(vector<Connection>::iterator it=connections.begin(); it != connections.end(); ++it){
		if(it->get_victim() == v_sid){
			if(_state == state_map("whostile"))
				// 'hostile' connection
				return false;
			else
				return true;
		}
	}
	return false;
}

void Server::new_connection(int v_sid, float arate, float distance, int state){
	bool connected = connection_exists(v_sid, state);
	if(connected  == true){
		string error = "Already connected to " + to_string(v_sid) + "from " + to_string(index) +". Something wrong with quantum.py";
		//throw runtime_error(error);
	}else{
		connections.push_back(Connection(index, v_sid, arate, distance, state));
	}
}

float Server::get_reserve(){
	return reserve;
}

float Server::get_invested(){
	return invested;
}

float Server::get_power(){
	return reserve + invested;
}

int Server::get_index(){
	return index;
}

pair<float,float> Server::get_pos(){
	return pos;
}

string Server::show(){
	string res;
    res = "("+to_string(pos.first)+","+to_string(pos.second)+") res:"+to_string(reserve)+",inv:"+to_string(invested)+",own:"+to_string(owner)+",lim:"+to_string(limit)+",ind:"+to_string(index);
    return res;
}
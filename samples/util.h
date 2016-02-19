/*
	DON'T EDIT THIS FILE
*/
#ifndef UTIL
#define UTIL

#include <iostream>
#include <string>
#include <utility>
#include <map>
#include <vector>
using namespace std;


int state_map(string state_str);
string inv_state_map(int state_index);


class Connection
{
private:
	int attacker;
	int victim;
	float full_distance;
	int state;
	float length;
public:
	float arate;
	Connection(	int _attacker, int _victim, float _arate, float _distance, int _state);

	void sync(float _arate,	int _state,	float _length);
	int get_attacker();
	int get_victim();
	int get_state();
	float get_full_distance();
	float get_length();
	string show();
};

class Server
{
private:
	pair<float,float> pos;
	float reserve;
	float invested;
	int index;
	
public:
	vector<Connection> connections;
	int owner;
	float limit;
	Server(	pair<float,float> _pos, float _power, float _maxpow, int _owner, int _index);
	void sync(float _reserve,float _invested,float _owner);
	bool connection_exists(int v_sid, int _state);
	void new_connection(int v_sid,float arate,float distance,int state);
	float get_reserve();
	float get_invested();
	float get_power();
	int get_index();
	pair<float,float> get_pos();
	//float update_pow(float dr,float di);
	//
	string show();
};
#endif
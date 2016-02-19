/*
 *	DONT EDIT THIS FILE
*/
#ifndef QUANTUM
#define QUANTUM

#include "util.h"
#include <iostream>
#include <sstream>
#include <string>
#include <map>
#include <cmath>
#include <vector>

using namespace std;

class ServerStack
{
public:
	float turntime, loadtime, actual_width, aspect, score;
	int turn, my_id, bot_count, server_count;
	bool active;
	map<int, vector<int> > Clusters;
	vector<Server>         Servers;
	vector<int>            enemy_nodes, neutrals, my_nodes;
	vector<vector<float> > news_deletions, news_additions, news_alerts;

	ServerStack();

	void setup(string start_data);
	vector<Connection>::iterator find_connection(int a_sid, int v_sid);
	vector<Connection>::iterator find_connection(int a_sid, int v_sid, int _state);
	void update_state(string up_data);

	float dist_between(int id1,int id2);

	void attack(int sid,int tid,float arate);
	void update_link(int sid,int tid,float arate);
	void withdraw(int sid,int tid,float split);
	void error_dump(string whatever);

	void pretty_dump_alerts();
	void pretty_dump_additions();
	void pretty_dump_deletions();
};
#endif
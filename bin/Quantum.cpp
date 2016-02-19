/*
 * DON'T EDIT THIS FILE!
 * This is the interface to the Game Engine
*/

#include "Quantum.h"

using namespace std;

vector<string> split(const string &s, char delim, vector<string> &elems) {
    stringstream ss(s);
    string item;
    while (getline(ss, item, delim)){
    	if (item != "")
        	elems.push_back(item);
    }
    return elems;
}


vector<string> split(const string &s, char delim) {
    vector<string> elems;
    split(s, delim, elems);
    return elems;
}

string trim(const string &s)
// not needed
{
    string::const_iterator it = s.begin();
    while (it != s.end() && isspace(*it))
        it++;

    string::const_reverse_iterator rit = s.rbegin();
    while (rit.base() != it && isspace(*rit))
        rit++;

    return string(it, rit.base());
}

/** End of helper functions **/

ServerStack::ServerStack(){
	turntime = 0;
	loadtime = 0;
	turn 	 = 0;
	score    = 0;
	active 	 = true;
}

void ServerStack::setup(string start_data){
	vector<string> lines = split(start_data,'\n');
	for(int i=0;i<lines.size();i++){
		//string line = trim(lines[i]);
		vector<string> details = split(lines[i],'~');
		string key = details[0];
		string data = details[1];
		if(key == "turn"){
			turn = stoi(data);
		}else if(key == "turntime"){
			turntime = stof(data);
		}else if(key == "loadtime"){
			loadtime = stof(data);
		}else if(key == "id" ){
			my_id = stoi(data);
		}else if(key == "act_width"){
			actual_width = stoi(data);
		}else if(key == "aspect"){
			aspect = stof(data);
		}else if((key == "n") || (key == "s")){
			vector<string> sdata = split(data,' ');
			int sid = stoi(sdata[0]);
			pair<float,float> pos;
			pos.first = stof(sdata[1]);
			pos.second = stof(sdata[2]);
			float reserve = stof(sdata[3]);
			float invested = stof(sdata[4]);
			float limit = stof(sdata[5]);
			int owner = stoi(sdata[6]);

			Servers.push_back(Server(pos, reserve+invested, limit, owner, sid));
			Clusters[owner].push_back(sid);
		}else if(key == "bot_count"){
			bot_count = stoi(data);
		}else if(key == "server_count"){
			server_count = stoi(data);
		}
	}
	if(active == true){
		my_nodes = Clusters[my_id];
		
		for(int i =0;i<Servers.size();i++){
			Server temp = Servers[i];
			if((temp.owner != my_id) and (temp.owner != -1)){
				enemy_nodes.push_back(temp.get_index());
			}
			if(temp.owner == -1){
				neutrals.push_back(temp.get_index());
			}
		}
	}
}

vector<Connection>::iterator ServerStack::find_connection(int a_sid, int v_sid){
	vector<Connection>::iterator it;
	for (it=Servers[a_sid].connections.begin(); it != Servers[a_sid].connections.end(); ++it){
		if(it->get_victim() == v_sid){
			return it;
		}
	}
	// now, it has become container.end()
	return it;
}

vector<Connection>::iterator ServerStack::find_connection(int a_sid, int v_sid, int _state){
	vector<Connection>::iterator it;
	for (it=Servers[a_sid].connections.begin(); it != Servers[a_sid].connections.end(); ++it){
		if (_state == 4){
			if(it->get_victim() == v_sid && it->get_state() == _state){
				return it;
			}
		}
		else{
			if(it->get_victim() == v_sid && (it->get_state() == _state || it->get_state() != 4)){
				return it;
			}
		}
	}
	// now, it has become container.end()
	return it;
}

void ServerStack::update_state(string up_data){
	news_deletions.clear();
	news_additions.clear();
	news_alerts.clear();
	
	vector<string> lines = split(up_data,'\n');
	map<int,vector<int> >_clusters;

	for(int i =0 ;i < lines.size();i++){
		//string line = trim(lines[i]);
		vector<string> details = split(lines[i],'~');
		string key = details[0];
		string data = details[1];
		if(key == "turn")
			turn = stoi(data);
		else if(key == "score")
			score = stof(data);
		else if(key == "s"){
			vector<string> sdata = split(data,' ');
			int sid = stoi(sdata[0]);
			float reserve = stof(sdata[1]);
			float invested = stof(sdata[2]);
			int owner = stoi(sdata[3]);
			Servers[sid].sync(reserve, invested, owner);
			_clusters[owner].push_back(sid);
		}
		else if(key == "end"){
			active = false;
			break;
		}
		else if(key == "cd"){
			vector<string> sdata = split(data,' ');
			float epoch_pct = stof(sdata[0]);
			int a_sid = stoi(sdata[1]);
			int _state = stoi(sdata[3]);
			int v_sid;
			if (_state == 4)
				// the vsid is decorated in quotes!
				// make sure we look for a 'whostile'
				v_sid = stoi(sdata[2].substr(1, sdata[1].length()-2));
			else
				v_sid = stoi(sdata[2]);
			//when deleting, need to use as much 'info' as possible for fingerprint

			vector<Connection>::iterator x_id = find_connection(a_sid, v_sid, _state);
			if( x_id != Servers[a_sid].connections.end()){
				Servers[a_sid].connections.erase(x_id);
				vector<float> temp = {epoch_pct,a_sid,v_sid,_state};
				news_deletions.push_back(temp);
			}else{
				;// I dont know what to do here. Throw error maybe?
			}
		}else if(key == "cn"){
			vector<string> sdata = split(data,' ');
			int a_sid = stoi(sdata[0]);
			float arate = stof(sdata[2]);
			float fdist = stof(sdata[3]);
			int _state = stoi(sdata[4]);
			int v_sid;
			if (_state == 4)
				// the vsid is decorated in quotes!
				v_sid = stoi(sdata[1].substr(1, sdata[1].length()-2));
			else
				v_sid = stoi(sdata[1]);
			Servers[a_sid].new_connection(v_sid, arate, fdist, _state);
			vector<float> temp = {(float)a_sid, (float)v_sid, arate, fdist, (float)_state};
			news_additions.push_back(temp);
		}else if(key == "c"){
			vector<string> sdata = split(data,' ');
			int a_sid = stoi(sdata[0]);
			float arate = stof(sdata[2]);
			int _state = stoi(sdata[3]);
			float length = stof(sdata[4]);
			int v_sid;
			vector<Connection>::iterator needs_update_id;
			if (_state == 4){
				// the vsid is decorated in quotes!
				v_sid = stoi(sdata[1].substr(1, sdata[1].length()-2));
				//'whostile' connections cannot convert, must use as fingerprint
				needs_update_id = find_connection(a_sid,v_sid, 4);
			}
			else{
				v_sid = stoi(sdata[1]);
				// for non-whostile, state might have changed too, can't use it as a fingerprint!
				needs_update_id = find_connection(a_sid,v_sid);
			}
			
			if(needs_update_id != Servers[a_sid].connections.end()){
				needs_update_id->sync(arate, _state, length);
			}
			else{
				;//again I dont know what to do with except part. Throw error maybe?
			}
		}else if(key == "A"){
			vector<string> sdata = split(data,' ');
			char _mode = sdata[0][0];
			int turn_no = stoi(sdata[1]);
			float epoch_pct = stof(sdata[2]);
			int info1 = stoi(sdata[3]);
			int info2 = stoi(sdata[4]);
			float info3 = stof(sdata[5]);
			if(_mode == 'w' || _mode == 'p'){
				info3 = (int)info3;
			}
			vector<float> temp = {(float)turn_no,epoch_pct,(float)_mode,(float)info1,(float)info2,(float)info3};
			news_alerts.push_back(temp);
		}	
	}
	Clusters = _clusters;
	if (active == true){
		my_nodes = Clusters[my_id];
		for(int i =0;i<Servers.size();i++){
			Server temp = Servers[i];
			if((temp.owner != my_id) and (temp.owner != -1)){
				enemy_nodes.push_back(temp.get_index());
			}
			if(temp.owner == -1){
				neutrals.push_back(temp.get_index());
			}
		}

	}
}

float ServerStack::dist_between(int id1,int id2){
	pair<float,float> pos1,pos2;
	pos1 = Servers[id1].get_pos();
	pos2 = Servers[id2].get_pos();
	return pow((pow((pos1.first - pos2.first)*actual_width,2) + pow((pos1.second - pos2.second)*(actual_width/aspect),2)),0.5);
}

void ServerStack::attack(int sid,int tid,float arate){
	cout << "a " << sid << " "<< tid << " " << arate << "\n";
	cout.flush();
}
void ServerStack::update_link(int sid,int tid,float arate){
	cout << "u " << sid << " "<< tid << " " << arate << "\n";
	cout.flush();
}
void ServerStack::withdraw(int sid,int tid,float split){
	cout << "w " << sid << " "<< tid << " " << split << "\n";
	cout.flush();
}

void ServerStack::error_dump(string whatever){
	cerr<<whatever<<endl;
	cerr.flush();
}

void ServerStack::pretty_dump_alerts(){
	vector<float> alert;
	if(news_alerts.size() > 0){
		for(int i=0;i<news_alerts.size();i++){
			alert = news_alerts[i];
			int turn_no = (int)alert[0];
			float epoch_pct = alert[1];
			char _mode = alert[2];
			int info1 = (int)alert[3];
			int info2 = (int)alert[4];
			float info3 = alert[5];
			string message;
			if(_mode == 'p'){
				message = to_string(info1)+"'s "+to_string(info2)+" pawned your server "+to_string((int)info3)+"! @ turn("+to_string(turn_no)+"+"+to_string(epoch_pct)+")";
			}else if(_mode == 'w'){
				message = "Server "+to_string(info1)+" is \"in-danger\". Game 'auto-withdrew' connection to "+to_string(info2)+" (state:'"+inv_state_map((int)info3)+"' @ turn("+to_string(turn_no)+"+"+to_string(epoch_pct)+")";
			}else if(_mode == 'i'){
				message = "Turn "+to_string(turn_no)+": Can't attack "+to_string((int)info1)+" from "+to_string((int)info2)+" due to insufficient resource. Needed "+to_string(info3);
			}
			error_dump(message);
		}
	}
}

void ServerStack::pretty_dump_additions(){
	vector<float> news;
	if(news_additions.size() > 0){
		for(int i=0;i<news_additions.size();i++){
			news = news_additions[i];
			int asid = news[0];
			int vsid = news[1];
			float arate = news[2];
			float fdist = news[3];
			int state = news[4];
			string message = "new connection from "+to_string(asid)+" to "+to_string(vsid)+" (arate="+to_string(arate)+"; fdist="+to_string(fdist)+" was made of type:"+inv_state_map(state)+" @ t"+to_string(turn);
			error_dump(message);
		}
	}
}

void ServerStack::pretty_dump_deletions(){
	vector<float> news;
	if(news_deletions.size()>0){
		for(int i=0;i<news_deletions.size();i++){
			news = news_deletions[i];
			float epct = news[0];
			int asid = news[1];
			int vsid = news[2];
			int state = news[3];
			string message = "Connection from "+to_string(asid)+" to "+to_string(vsid)+" of type:"+inv_state_map(state)+" was deleted @ t"+to_string(turn)+"+"+to_string(epct);
			error_dump(message);
		}
	}
}
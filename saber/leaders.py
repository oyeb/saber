import trueskill, pymysql

class Leaderboard:
	def __init__(self):
		self.env = trueskill.TrueSkill()
		self.conn = pymysql.connect(host='localhost', user='ananya', passwd='ScherbiuS', db='bob')
		self.cur = self.conn.cursor()

		self.cur.execute("select * from teams;")
		self.teams_dict = {}
		for team in self.cur.fetchall():
			tobj = {"id"     : team[0],
					"name"   : team[1],
					"rating" : self.env.create_rating(mu=team[2], sigma=team[3])}
			self.teams_dict[team[0]] = tobj

	def show_board(self):
		all_teams = [team for team in self.teams_dict.values()]
		leaderboard = sorted(all_teams, key=lambda team: self.env.expose(team['rating']), reverse=True)
		[print(team['id'], team['rating'].mu) for team in leaderboard]

	def do_rating(self, team_ids, scores, status, pturns, weights=None):
		sm = []
		for st in status:
			if st in ('timeout', 'crashed'):
				sm.append(0)
			if st == 'eliminated':
				sm.append(1)
			elif st == 'survived':
				sm.append(2)
		zipped = [(sm[i], scores[i], pturns[i], team_ids[i]) for i in range(len(team_ids))]
		rgroup = sorted(zipped, reverse=True)
		print("PPPP", rgroup)

		rating_for = []
		for s, pt, score, tid in rgroup:
			rating_for.append((self.teams_dict[tid]['rating'],))

		rated_groups = self.env.rate(rating_for, weights=weights)
		self.save_ratings(rgroup, rated_groups)
		return [(rgroup[i], rated_groups[i][0].mu, rated_groups[i][0].sigma) for i in range(len(rated_groups))]

	def save_ratings(self, rgroup, rated_groups):
		for i in range(len(rgroup)):
			self.teams_dict[rgroup[i][3]]['rating'] = rated_groups[i][0]

	def commit(self, tname):
		for tobj in self.teams_dict.values():
			upq = "update %s set rating_mu = "%tname+str(tobj['rating'].mu)+", rating_sigma = "+str(tobj['rating'].sigma)+" where teams.team_id = %d;" % tobj['id']
			print(upq)
			self.cur.execute(upq)
		self.conn.commit()
import house
import os

s = house.get_sandbox(os.getcwd())
s.start("bash ./bot_launch_cmd_file")
print("SandBox started")
s.pause()
print('SandBox has been sent signal "STOP", (it\'s paused)')

ch = input("It should list all files now.\nPress enter to resume it!\n>")
s.resume()
while True:
	l = s.read_line()
	if l != None:
		l = l.strip('\r\n')
		if l.lower() == "done":
			break
		print(l)

print(s.is_alive)
if s.is_alive:
	s.kill()
s.release()
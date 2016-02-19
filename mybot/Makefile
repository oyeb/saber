DEPS = util.h Quantum.h bot_template.h
PROD = util.o bot_launcher.o bot_template.o Quantum.o

%.o: %.cpp $(DEPS)
	g++ -c -o $@ $< -Wall -std=c++14  -lm

bot_launcher.prog: $(PROD)
	g++ -std=c++14 -Wall -o $@ $^

clean:
	rm *.o *.prog
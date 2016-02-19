DEPS = util.h Quantum.h special.h donothing.h hard_coded.h
HC = util.o Quantum.o hard_coded.o hard_coded_launcher.o
SPEC = util.o Quantum.o special.o special_launcher.o
DN = util.o Quantum.o donothing.o donothing_launcher.o

%.o: %.cpp $(DEPS)
	g++ -c -o $@ $< -Wall -std=c++14 -lm

hard_coded_launcher.prog: $(HC)
	g++ -std=c++14 -Wall -o $@ $^

special_launcher.prog: $(SPEC)
	g++ -std=c++14 -Wall -o $@ $^

donothing_launcher.prog: $(DN)
	g++ -std=c++14 -Wall -o $@ $^

all_samples: hard_coded_launcher.prog special_launcher.prog donothing_launcher.prog

clean:
	rm *.o *.prog
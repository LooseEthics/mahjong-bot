TARGET = tenpai_gen
CXX = g++
SRCS = tenpai_gen.cpp
OBJS = $(SRCS:.cpp=.o)
CXXFLAGS = -O2 -Wall

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LIBS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

.PHONY: clean
clean:
	rm -f *.o $(TARGET)

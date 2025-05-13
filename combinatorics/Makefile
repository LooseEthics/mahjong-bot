TARGET = recurse_cnt
CXX = g++
SRCS = recurse_cnt.cpp multiset_math.cpp
OBJS = $(SRCS:.cpp=.o)
LIBS = -lgmpxx -lgmp
CXXFLAGS = -O2 -Wall

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LIBS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

.PHONY: clean
clean:
	rm -f *.o $(TARGET)

#include <iostream>
#include <string>
#include <vector>
#include <stdlib.h>
#include <time.h>
#include "data_generation.h"
using namespace std;

void generate(int size,vector<char>&msg) {
	srand(time(NULL));
	


	for (int i = 0; i < size; i++) {

		msg[i] = symbols[rand() % 38]; // ������� ��������� ������ �� data_generation.h

	}


}

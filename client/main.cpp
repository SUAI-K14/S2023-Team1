// Client part for Server-Client chat. Developed by Mr_Dezz, modified by Emil, Misha, Kostya and Dima

#include <iostream> //потоковый ввод-вывод
#include <WinSock2.h> // для работы с сокетами
#include <WS2tcpip.h> // для работы с tcp/i[
#include <inaddr.h> //не знаю
#include <stdio.h> // для fgets
//#include <vector> // для работы с векторами
#include <windows.h> //для sleep
#include "data_generation.h" // для второго (случайного) типа сообщений	
#include "main.h" // заголовочный файл main
#include <string>

#pragma comment(lib, "ws2_32.lib")

using namespace std;


int main(void)
{
	//Key constants
	const char SERVER_IP[] = "127.0.0.1";					// Enter IPv4 address of Server
	const short SERVER_PORT_NUM = 1;				// Enter Listening port on Server side
	const short BUFF_SIZE = 1024;					// Maximum size of buffer for exchange info between server and client
	MSG_num = 1;
	// Key variables for all program
	int erStat;										// For checking errors in sockets functions

	//IP in string format to numeric format for socket functions. Data is in "ip_to_num"
	in_addr ip_to_num;
	inet_pton(AF_INET, SERVER_IP, &ip_to_num);


	// WinSock initialization
	WSADATA wsData;
	erStat = WSAStartup(MAKEWORD(2, 2), &wsData);

	if (erStat != 0) {
		cout << "Error WinSock version initializaion #";
		cout << WSAGetLastError();
		return 1;
	}
	else
		cout << "WinSock initialization is OK" << endl;

	// Socket initialization
	SOCKET ClientSock = socket(AF_INET, SOCK_STREAM, 0);

	if (ClientSock == INVALID_SOCKET) {
		cout << "Error initialization socket # " << WSAGetLastError() << endl;
		closesocket(ClientSock);
		WSACleanup();
	}
	else
		cout << "Client socket initialization is OK" << endl;

	// Establishing a connection to Server
	sockaddr_in servInfo;

	ZeroMemory(&servInfo, sizeof(servInfo));

	servInfo.sin_family = AF_INET;
	servInfo.sin_addr = ip_to_num;
	servInfo.sin_port = htons(SERVER_PORT_NUM);

	erStat = connect(ClientSock, (sockaddr*)&servInfo, sizeof(servInfo));

	if (erStat != 0) {
		cout << "Connection to Server is FAILED. Error # " << WSAGetLastError() << endl;
		closesocket(ClientSock);
		WSACleanup();
		return 1;
	}
	else
		cout << "Connection established SUCCESSFULLY. Ready to send a message to Server" << endl;


	//Exchange text data between Server and Client. Disconnection if a Client send "xxx"

	vector <char> servBuff(BUFF_SIZE), clientBuff(BUFF_SIZE);// Buffers for sending and receiving data
	short packet_size = 0; // The size of sending / receiving packet in bytes
	/*cout << "Enter username:" << endl;
	fgets(clientBuff.data(), clientBuff.size(), stdin);
	packet_size = send(ClientSock, clientBuff.data(), clientBuff.size(), 0);
	*/

	while (true) {

		cout << "Select the type of message you would like to send.\n\t1 - custom message, 2 - generated message" << endl;
		cin >> TypeOfMSG;
		if (TypeOfMSG == 1) {
			cout << "You chose type " << TypeOfMSG << endl;
			cout << "Enter your message:" << endl;
			while ((getchar()) != '\n'); //This will consume the '\n' char
			//now you're free to use fgets
			fgets(clientBuff.data(), clientBuff.size(), stdin); // Ввод сообщения
			// Check whether client like to stop chatting
			if (clientBuff[0] == 'x' && clientBuff[1] == 'x' && clientBuff[2] == 'x') { // здесь проверяем хочет ли юзер перестать общаться
				shutdown(ClientSock, SD_BOTH);
				closesocket(ClientSock);
				WSACleanup();
				return 0;
			}
			else {
				
				packet_size = send(ClientSock, clientBuff.data(), clientBuff.size(), 0); //Отправка сообщения
			}
		}
		else if (TypeOfMSG == 2) {
			cout << "You chose type " << TypeOfMSG << endl;
			cout << "Choose length of your message" << endl;
			cin >> MSGSize; // выбираем длину
			cout << "Choose how many messages to send" << endl;
			cin >> MSG_num; // выбираем количество
			cout << "Choose the periodicity of your message (how often do you send it), in seconds" << endl;
			cin >> P; // выбираем периодичность (как часто в секундах отправлять)
			for (int i = 0; i < MSG_num; i++) {
				Sleep(P * 1000); // задержка в секундах
				cout << "Message #" << i + 1 << " ";
				generate(MSGSize, clientBuff); // генерируем сообщение
				for (int j = 0; j < MSGSize; j++) {
					cout << clientBuff[j]; // выводим его
				}
				cout << "\n";
				packet_size = send(ClientSock, clientBuff.data(), clientBuff.size(), 0); // отправляем











			}
		}
		else cout << "Please select correct type!" << endl; // выберите правильный тип










		if (packet_size == SOCKET_ERROR) {
			cout << "Can't send message. Error # " << WSAGetLastError() << endl;
			closesocket(ClientSock);
			WSACleanup();
			return 1;
		}

		packet_size = recv(ClientSock, servBuff.data(), servBuff.size(), 0);

		if (packet_size == SOCKET_ERROR) {
			cout << "Can't receive message. Error # " << WSAGetLastError() << endl;
			closesocket(ClientSock);
			WSACleanup();
			return 1;
		}
		else
			cout << "Server: " << servBuff.data() << endl;

	}

	closesocket(ClientSock);
	WSACleanup();

	return 0;
}


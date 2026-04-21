#include <iostream>
#include <map>
using namespace std;

int main() {
    map<string, string> arpTable;
    arpTable["192.168.1.1"] = "AA:BB:CC:DD:EE:01";
    arpTable["192.168.1.2"] = "AA:BB:CC:DD:EE:02";
    arpTable["192.168.1.3"] = "AA:BB:CC:DD:EE:03";

    string ip;
    cout << "Enter IP Address: ";
    cin >> ip;

    if (arpTable.find(ip) != arpTable.end()) {
        cout << "MAC Address: " << arpTable[ip] << endl;
    } else {
        cout << "IP not found in ARP table\n";
    }

    return 0;
}
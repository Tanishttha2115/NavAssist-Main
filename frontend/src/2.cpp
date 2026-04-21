#include <iostream>
#include <map>
using namespace std;

int main() {
    map<string, string> rarpTable;
    rarpTable["AA:BB:CC:DD:EE:01"] = "192.168.1.1";
    rarpTable["AA:BB:CC:DD:EE:02"] = "192.168.1.2";
    rarpTable["AA:BB:CC:DD:EE:03"] = "192.168.1.3";

    string mac;
    cout << "Enter MAC Address: ";
    cin >> mac;

    if (rarpTable.find(mac) != rarpTable.end()) {
        cout << "IP Address: " << rarpTable[mac] << endl;
    } else {
        cout << "MAC not found in RARP table\n";
    }

    return 0;
}
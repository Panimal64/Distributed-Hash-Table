# DHT
Distributed Hash Table similar to Chord. DHT node stores data and communicates with other nodes
using peer-to-peer system.  DHT client is command line tool users can use to read and write data into system

Node joining is not implemented, when launching node will take two command line parameters
dht_node.py [HOST_FILE] [LINE_NUM]
Each line of host file contains node address and portnumber in xx.xxxxxx.edu 12345 format starting at line 0

Client will take 4 or 5 command line parameters
dht_node.py [NODE_ADDRESS] [NODE_PORT] [get|put] [KEY] [VALUE]

EXAMPLE:

dht_node.py xx.xxxx.edu 12345 put Washington Olympia

dht_node.py xx.xxxx.edu 12345 get Washington

Delete a key:value
dht_node.py xx.xxxx.edu 12345 put Washington

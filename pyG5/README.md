## pyG5Network.py
### class pyG5NetWorkManager
socket auf anyIP4 address port = 0 (system will actually assign a free port number)
when connected: -> call socketStateHandler() 
#### socketStateHandler()
creates `pyG5MulticastListener`, connect its signal output (`xpInstance=Signal(QHostAddress, int)`) to own  xplaneConnect(self, addr, port)

listens to a 5-character MESSAGE PROLOGUE `BECN\0` which indicates the type of the following struct as
```c
struct becn_struct
{
    uchar beacon_major_version; // 1 at the time of X-Plane 10.40
    uchar beacon_minor_version; // 2 at the time of X-Plane 11.50, adds the RakNet port number
    xint application_host_id; // 1 for X-Plane, 2 for PlaneMaker
    xint version_number; // 104103 for X-Plane 10.41r3
    uint role; // 1 for master, 2 for extern visual, 3 for IOS
    ushort port; // port number X-Plane is listening on, 49000 by default
    xchr computer_name computer_name[500]; // the hostname of the computer, e.g. “Joe’s Macbook”, null-
    terminated string
    ushort raknet_port; // port number the X-Plane Raknet client is listening on, default is
    49010
};
```
- XCHR (character, in local byte-order for the machine you are on)
- XINT (4-byte int, in local byte-order for the machine you are on)
- XFLT (4-byte ints and floats, in local byte-order for the machine you are on)
- XDOB (double-precision float, in local byte-order for the machine you are on)


### class pyG5MulticastListener
listens to the "BECN" message that contains xplane's address and port
sends address an port via signal to `pyG5NetWorkManager.xplaneConnect(self, addr, port)`
and closes its port 

### back to class pyG5NetWorkManager
####  pyG5NetWorkManager.xplaneConnect(self, addr, port)
- disconnects from pyG5MulticastListener.xpInstance because addr and port of xplane is now known
- init connection to xplane by sending all dataref's it whats to get messages about to xplane 
##### message send to xplane
for each element of the datarefs :

struct dref_struct_in
{
    xint dref_freq;
    xint dref_sender_index; // the index the customer is using to define this dataref
    xchr dref_string[400];
};

```python 
 # ( dataref 0 , frequency 1, unit, description, num decimals to display in formatted output )
            (
                "sim/cockpit/radios/nav1_dme_dist_m",
                30,
                "kt",
                "dme Range anv1",
                0,
                "_nav1dme",
            ),...
```
it sends : 
`b"RREF\x00"` (request ref ) plus frequency (`30`) a as a number plus the name but encoded() (`"sim/cockpit/radios/nav1_dme_dist_m"`) plus the idx of the dataref , using 
` message = struct.pack("<5sii400s", cmd, freq, idx, ref)`  so that the message is exacly  
`assert len(message) == 413` long 

```python
import struct
cmd = b"RREF\x00"
freq = 30
ref = "sim/cockpit/radios/nav1_dme_dist_m".encode()
idx = 0
message = struct.pack("<5sii400s", cmd, freq, idx, ref)
```
The format string "<5sii400s" specifies how to pack the data:
- '<' means use little-endian byte order
- '5s' means a 5-byte string (our cmd)
- 'i' means a 4-byte integer (our freq)
- Another 'i' for another 4-byte integer (our idx)
- '400s' means a 400-byte string (our ref, padded or truncated to 400 bytes)




## SCREEN Test

### System and enviroment.
* system
  * this program run on linux
* requirements
  * pexpect<br>
      pexpect is requried. due to we need pexpect to connect dhcp server to get dhcp_release list.
  * dhcp<br>
      in this program we will use dhcp service. so that we can get the test unit ipaddress via mac.<br>
    you can install the dhcp service in test pc or another pc.
* How to get the program<br>
  ```
  git clone git@github.com:tahyuu/SCREEN.git SCREEN
  ```
* How to Config the program.
  * copy the file /SCREEN/bin/list_dhcp_release to /bin<br>
    ```
    copy /SCREEN/bin/list_dhcp_release /bin
    ```
    
* How to run the program
  ```
  cd SCREEN
  ./screen.py
  ```
  after that you need input Serial Number, BMC MAC, Thermal part temp<br>
* Where is test log.<br>
  you can find test log in SCREEN/TestLog/.
  you can also find the test result summry in SCREEN/data.csv
  
  
* How to install NI-VISA
```
yum -y install libstdc++
yum -y install glibc.i686
yum -y install libstdc++.i686
mkdir NI
mount -o loop NI-VISA-17.0.0.iso NI
./INSTALL
```
  

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
  git clone git@github.com:tahyuu.screen.git SCREEN
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
  

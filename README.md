## SCREEN Test

### System and enviroment.
* Hareware config. you can reference below image

* system
  * this program run on linux
  we are using centos 1804. please download the os image from below link<br>
  http://isoredirect.centos.org/centos/7/isos/x86_64/CentOS-7-x86_64-DVD-1804.iso
* requirements
  * pexpect<br>
      pexpect is requried. due to we need pexpect to connect dhcp server to get dhcp_leases list.
      you can follow below command to install pexpect
      ```
      yum -y install epel-release
      yum -y install python-pip
      pip install --upgrade pip
      pip install pexpect
      ```
  * dhcp<br>
      in this program we will use dhcp service. so that we can get the test unit ipaddress via mac.<br>
    you can install the dhcp service in test pc or another pc.
      you can config a dhcp server as below step. first of all make sure you can access the internet. then excute below command.
      assuming that you are using eth0 as dhcp server port.
      ```
      cd ~
      git clone git@github.com:tahyuu/SCREEN.git SCREEN
      cd ~/SCREEN/Install
      ./install_dhcp.sh eth0 192.168.4.2
      ```
      
* How to get the program<br>
 please note that if you already get the program when you install dhcp server. please ignore it.
  ```
  git clone git@github.com:tahyuu/SCREEN.git SCREEN
  ```

* Config the program.<br>
  you can config the progam via ~/SCREEN/config.ini. for more detail please open ~/SCREEN/config.ini.
      
* How to run the program
  ```
  cd ~/SCREEN
  ./screen.py
  ```
  after that you need input Serial Number, BMC MAC, Thermal part temp<br> the program wil start


* Where is test log.<br>
  you can find test log in SCREEN/TestLog/.
  you can also find the test result summry in SCREEN/data.csv<br><br><br><br><br><br><br><br><br>
  
<font color="#FF0000">##################################################################################<br>
below install is prepare for auto 34970A read. not ready now. you can ignore below<br>
##################################################################################<br></font>
* How to install NI-VISA
```
####################
#update kernel
####################
cd /root/SCREEN/Install/rpm_file
yum -y install kernel-lt-4*
yum -y install kernel-lt-devel-4*
####################
#install libstdc++
####################
yum -y install libstdc++
yum -y install glibc.i686
yum -y install libstdc++.i686
####################
#install NI VISA
####################
cd /root/SCREEN/Install
mkdir NI
mount -o loop NI-VISA-17.0.0.iso NI
./INSTALL
```
  

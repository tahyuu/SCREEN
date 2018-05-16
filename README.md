## SCREEN Test

### System and enviroment.

* HardWare List.<br>
  1, PC with Eth port as Tester.<br>
  2, PC with Eth Port as DHCP Server. you an also use One PC as DHCP sever and also as Tester. below hardware config is based assuming that the DHCP server and Tester are one PC.<br>
  3, Switch.<br>
  4, Eth Cable.<br>
  
* Hareware config. you can reference below image
![Image text](https://github.com/tahyuu/SCREEN/blob/master/SOP/HarwareConfig.png)
* [Tester/DHPC SERVER]system
  * this program run on linux
  we are using centos 1804. please download the os image from below link<br>
  http://isoredirect.centos.org/centos/7/isos/x86_64/CentOS-7-x86_64-DVD-1804.iso
* [TESTER]system requirements
  * pexpect<br>
      pexpect is requried. due to we need pexpect to connect dhcp server to get dhcp_leases list.
      you can follow below command to install pexpect
      ```
      yum -y install epel-release
      yum -y install python-pip
      pip install --upgrade pip
      pip install pexpect
      yum install OpenIPMI
      yum install ipmitool
      ```
  * How to setup dhcp server<br>
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
  you can config the progam via ~/SCREEN/config.ini. for more detail please open ~/SCREEN/config.ini.<br>
  update it as follow in DHCP section.<br>
  
```python
  [DHCP]
#config the dhcp server ip. if the dhcp server is localhost we will read file from localhost.
##############################################################
# below dhcp config is for zhuhai site
##############################################################
#dhcp_server=            192.168.4.3
#dhcp_leases_root=           "~/dhcpd.leases"
#dhcp_user_name=         dhcp
#dhcp_password=          dhcp
##############################################################
# below dhcp config is for US 
# assuming that the dhcp server is the tester it is self, so config the dhcp_server to localhost.
# assuming that the dhcp user name and password are boot and 123456. please update it according
# assuming dhcpd.leases is in /var/lib/dhcpd/dhcpd.leases
##############################################################
dhcp_server=           localhost
dhcp_leases_root=      /var/lib/dhcpd/dhcpd.leases
dhcp_user_name=        root
dhcp_password=         123456
```
  
  
* How to run the program
  ```
  cd ~/SCREEN
  ./screen.py
  ```
  after that you need input Serial Number, BMC MAC, Thermal part temp<br> the program wil start. for more information you can see the SOP/Cannonball MB thermal sensor screen process instruction_0508.pdf


* Where is test log.<br>
  you can find test detail log in SCREEN/FTLog/.
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
  

# u103_atm_option_exit_program



## Run the application 
cd bin  
./easy-run.bat

./start-web.bat

### Web address
web page  
http://localhost:5173/   

back end server:  
http://127.0.0.1:5103  


## Deploying Release 1.2   

instructions:  
-- stop the application  ( close all three dos windows)  
-- run below command   
   cd c:\code\u103_atm_option_exit_program    
-- run below command:   
   git pull      
-- now the latest code is checked out  
--  

now you can run application based on instruction on 

Fixes:  
 -- The app cancels the open order  if the strike matches and cancels right before sending clsoe order.  


## Deploying Release 1.1

instructions:  
-- stop the application  ( close all three dos windows)  
-- run below command   
   **cd c:\code\u103_atm_option_exit_program**  
-- run below command:   
   **git pull**   
-- now the latest code is checked out  

now you can run application based on instruction on 

Fixes:  
 -- The application cancels SPXW open option orders before closing the open orders.  



## Deploying Release 1.0

it is done in the call ...



## Preparing environment
This is one time activity to setup the environment 

### Remote access 

we need either rust desk or teamviewer  
rustdesk:  https://rustdesk.com/  

### install python 
https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe


### install git 

https://git-scm.com/downloads/win


### install node.js

https://nodejs.org/en/download 

### Steps 
in the C: drive   
mkdir code  
cd code   
git checkout https://github.com/SaeedBohlooli/u103_atm_option_exit_program.git  
cd u103_atm_option_exit_program  
python -version  
pip install -r requirements.txt  


### TWS
Make it like below

![img.png](docs/img.png)  
![img.png](docs/img_1.png)  



### Architecture

- The suer enters the paramertrs in the web page and clicks submit  
- The backend (Flask) app catches paramerts and writes into shared/parameter.json   
- The engin reads the file every 15 seconds and evaluates conditions ...  
- 
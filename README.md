# UVT BRANDING APP

## Perequisites:

* [Visual Studio Code](https://code.visualstudio.com/download)
* The following extensions for VSCode:
    * Github Pull Requests
    * Pylance
    * Python
    * Python Debugger
    * Python Enviorment
    * HTML Boilerplate
    * HTML CSS Support
    * Javascript and Typescript Nightly
    * SQLite Viewer
    * SQLTools
    * SQLTools SQLite
    * SQLTools Mysql/MariaDB/TiDB
* [Git](https://git-scm.com/install/windows)
* [Python 3.14.x](https://www.python.org/downloads/)

## Clone the repo
* Clone [this](https://github.com/Robert-Csatlos/UVTBrandingApp) repo

![!! Image githubClone.png not found in /images/ !!](/images/githubClone.png "Click on the 2 squares.")

* Open up the source controll in VSCode clocking the following icon:

![!! Image sourceControll.png not found in /images/ !!](/images/sourceControll.png "clone the repo and open it")

* Configure the git in VSCode terminal using these 2 lines:
```
git config --global user.email "yourEmail@e-uvt.ro"
```
```
git config --global user.name "Your Name"
```

## Install Python 
* In the VSCode terminal use this command:
```
code --install-extension ms-python.python
```

* Install the virtual enviorment
```
python -m venv venv
```
_or_
```
py -m venv venv
```

* Activate venv
```
.\venv\Scripts\activate
```

* Install the python libraries:
```
pip install fastapi uvicorn sqlalchemy databases 'pydantic[email]'
```

### Now just run the main.py with the following command
```
python.exe .\main.py
```
To close the server use the combination (CTRL+C) in the Terminal where the server is on.
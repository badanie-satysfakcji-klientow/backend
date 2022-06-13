# Badanie-satysfakcji-klientow backend app
## Automatic setup
just use windows-setup.sh
to do so follow the instructions below
```bash
chmod +x windows-setup.sh
./windows-setup.sh
```
or for linux users
```bash
chmod +x linux-setup.sh
./linux-setup.sh
```

everything should work fine, if not try the manual way
## Manual setup development app
```bash
git clone https://github.com/badanie-satysfakcji-klientow/backend.git
cd backend
git checkout develop
```

#### setup .env file
can be found in **[Discord message](https://discord.com/channels/945475529459531846/951710824865611778/984114466528563230)**
or downloaded directly with this command:
```bash
curl.exe --output backend/.env https://cdn.discordapp.com/attachments/951710824865611778/986010602008891472/env
```

#### install python:
We're using **[python 3.10](https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe)** so we recommend using that version.

For other Windows releases follow that link: **[python versions](https://www.python.org/downloads/windows/)**

on linux
```bash
sudo apt-get install python3.10
```

#### install pip:
```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
python -m pip install --upgrade pip
```

or linux
```bash
sudo apt-get install python3-pip
```

#### install dependencies:
```bash
python -m pip install Django django-environ djangorestframework django-background-tasks rest_framework
```

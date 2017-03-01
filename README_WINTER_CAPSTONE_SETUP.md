# Winter Capstone Setup

## Connect to the PDX VPN and Windows Remote Desktop
- [PDX VPN Setup](https://cat.pdx.edu/linux/connecting-to-the-cecs-pptp-vpn.html)
- [PDX Windows Remote Desktop](https://cat.pdx.edu/windows/remote-desktop-access.html)

## Connect to our capstone PDX shell
You should already have access, if not, talk to Evan or Aaron.

## Launch the backend server
```
cd legacy_project/Simulated-Conversations/
vagrant up
vagrant ssh
cd /vagrant/vagrant/
python manage.py runserver 0.0.0.0:8258
```

## Interact with the webpage
From your PDX Windows Remote Desktop session, navigate to http://131.252.217.152:8258 with the web browser.
Get the username/password for the web UI from Aaron

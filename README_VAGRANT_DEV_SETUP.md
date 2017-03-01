# Vagrant Development Setup

## Warning
The following setup steps are not suitable for production.

## First Time Setup

### Dependencies

- VirtualBox
- Vagrant

### Launch/Initialize the VM
```
cd Simulated-Conversations/
vagrant up
```

### Setup the Simulated Conversations backend
```
vagrant ssh
cd /vagrant/vagrant/
python manage.py collectstatic
python manage.py syncdb
```

## Run the server

### Launch the Simulated Conversations backend server
```
cd Simulated-Conversations/
vagrant up
vagrant ssh
cd /vagrant/vagrant/
python manage.py runserver 0.0.0.0:8258
```

# 1. Initial Server Setup (as root)

```
ssh root@your-server-ip
```
```
apt update && apt upgrade -y
```
```
apt install python3 python3-pip python3-venv nginx git build-essential -y
```
```
adduser ali
CpG#A6&K[652
usermod -aG sudo ali
```

#  2. Application Setup (as the new user ali)

```
su - ali
```
```
git clone -b main https://github.com/shahrokh-rhmani/flask-sql-injection.git
mv flask-sql-injection sql-injection
cd sql-injection/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
```
python src/app.py
deactivate
exit
```

# 3. Configuring Gunicorn and Systemd (as root)

```
nano /etc/systemd/system/flaskapp.service
```
```
[Unit]
Description=Gunicorn instance to serve the Flask SQL Injection App
After=network.target

[Service]
User=ali
Group=www-data
WorkingDirectory=/home/ali/sql-injection/src
Environment="PATH=/home/ali/sql-injection/venv/bin"
ExecStart=/home/ali/sql-injection/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:flaskapp.sock \
          --timeout 120 \
          app:app

[Install]
WantedBy=multi-user.target
```
```
systemctl start flaskapp
systemctl enable flaskapp
```
```
systemctl status flaskapp
```

# 4. Configuring Nginx (as root)

```
nano /etc/nginx/sites-available/flaskapp
```
```
server {
    listen 80;
    server_name 82.115.20.217; # Change this to your server's IP or domain

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ali/sql-injection/src/flaskapp.sock;
    }
}
```
```
ln -s /etc/nginx/sites-available/flaskapp /etc/nginx/sites-enabled/
```
```
nginx -t
systemctl restart nginx
```

# 5. Permission Fixes (Crucial Step!) (as root)

Goal: Ensure Nginx (user www-data) has permission to read and write to the socket file created by Gunicorn (user ali).

### 1. Check the current permissions of the socket file (it might not exist until the service is running):
```
ls -la /home/ali/sql-injection/src/flaskapp.sock
```

### 2. Set the correct group ownership and permissions on the socket file:
```
chown ali:www-data /home/ali/sql-injection/src/flaskapp.sock
chmod 660 /home/ali/sql-injection/src/flaskapp.sock
```

### 3. Ensure Nginx's user (www-data) has execute (traverse) permissions on all parent directories to reach the socket:
```
chmod 755 /home/ali/
chmod 755 /home/ali/sql-injection/
chmod 755 /home/ali/sql-injection/src/
```

### 4. Restart the services to recreate the socket with the correct permissions:
```
systemctl restart flaskapp
systemctl restart nginx
```

### 5. Verify that Nginx can now see the socket file:
```
sudo -u www-data ls -la /home/ali/sql-injection/src/flaskapp.sock
```

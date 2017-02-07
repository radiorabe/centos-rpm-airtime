# CentOS 7 RPM Specfile for airtime

This repository contains the specfile for airtime which is part of the [obs build](https://build.opensuse.org/project/show/home:radiorabe:airtime) of the
[RaBe airtime fork](https://github.com/radiorabe/airtime).

## Quickstart

The following instructions show how to get up and running quickly. To deploy these packages on production you will have to review
the default policies of the packages and adapt them to your organizations policies.

### Install repositories

```bash
# install dependencies
yum install epel-release centos-release-scl
yum install http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-5.el7.nux.noarch.rpm
curl -o /etc/yum.repos.d/liquidsoap.repo \
  http://download.opensuse.org/repositories/home:/radiorabe:/liquidsoap/CentOS_7/home:radiorabe:liquidsoap.repo
# install airtime repo
curl -o /etc/yum.repos.d/airtime.repo \
  http://download.opensuse.org/repositories/home:/radiorabe:/airtime/CentOS_7/home:radiorabe:airtime.repo
```

### Database Setup

```bash
yum install postgresql-server

postgresql-setup initdb

patch /var/lib/pgsql/data/pg_hba.conf << EOD
--- /var/lib/pgsql/data/pg_hba.conf.orig2016-09-01 20:45:11.364000000 -0400
+++ /var/lib/pgsql/data/pg_hba.conf2016-09-01 20:46:17.939000000 -0400
@@ -78,10 +78,11 @@
 
 # "local" is for Unix domain socket connections only
 local   all             all                                     peer
+local   all             all                                     md5
 # IPv4 local connections:
-host    all             all             127.0.0.1/32            ident
+host    all             all             127.0.0.1/32            md5
 # IPv6 local connections:
-host    all             all             ::1/128                 ident
+host    all             all             ::1/128                 md5
 # Allow replication connections from localhost, by a user with the
 # replication privilege.
 #local   replication     postgres                                peer
EOD

systemctl enable postgresql
systemctl start postgresql

# create database user airtime with password airtime
useradd airtime
echo "airtime:airtime" | chpasswd

su -l postgres bash -c 'createuser airtime'
su -l postgres bash -c 'createdb -O airtime airtime'

echo "ALTER USER airtime WITH PASSWORD 'airtime';" | su -l postgres bash -c psql
echo "GRANT ALL PRIVILEGES ON DATABASE airtime TO airtime;" | su -l postgres bash -c psql
```

### RabbitMQ Setup

```bash
yum install https://github.com/rabbitmq/rabbitmq-server/releases/download/rabbitmq_v3_6_5/rabbitmq-server-3.6.5-1.noarch.rpm

systemctl enable rabbitmq-server
systemctl start rabbitmq-server

rabbitmqctl add_user airtime airtime
rabbitmqctl add_vhost /airtime
rabbitmqctl set_permissions -p /airtime airtime ".*" ".*" ".*"
```

### Airtime Web

```bash
yum install airtime-web

setsebool -P httpd_can_network_connect 1
setsebool -P httpd_execmem on # needed by liquidsoap to do stuff when called by php

mkdir /etc/airtime /srv/airtime /var/log/airtime/ /tmp/plupload
chcon -R -t httpd_sys_rw_content_t /etc/airtime/
chcon -R -t httpd_sys_rw_content_t /srv/airtime/
chcon -R -t httpd_sys_rw_content_t /var/log/airtime/
chcon -R -t httpd_sys_rw_content_t /tmp/plupload
chown -R apache /etc/airtime/ /srv/airtime/ /var/log/airtime/ /tmp/plupload

cat > /etc/php.d/99-tz.ini <<EOD
[main]
date.timezone=Europe/Zurich
EOD

systemctl enable httpd
systemctl start httpd

firewall-cmd --zone=public --add-port=80/tcp --permanent
firewall-cmd --reload
```

### Airtime Icecast

```bash
# TBD
```

### Airtime Playout

```bash
# TBD
```

### Airtime Liquidsoap

```bash
# TBD
```

### Airtime Media-Monitor

```bash
yum intall airtime-media-monitor

mkdir /srv/airtime/stor/{problem_files,organize,imported}
chown airtime-media-monitor:apache /srv/airtime/stor/{problem_files,organize,imported}
chmod g+w /srv/airtime/stor/{problem_files,organize,imported}

systemctl enable airtime-media-monitor
systemctl start airtime-media-monitor
```

### Airtime Silan

```bash
yum install airtime-silan

# run it manually
airtime-silan

# or let systemd run it once per hour
systemctl start airtime-silan.timer
systemctl enable airtime-silan.timer
```

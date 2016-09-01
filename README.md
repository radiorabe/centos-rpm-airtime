# CentOS 7 RPM Specfile for airtime

This repository contains the specfile for airtime which is part of the [obs build](https://build.opensuse.org/project/show/home:radiorabe:airtime) of the
[RaBe airtime fork](https://github.com/radiorabe/airtime).

## Usage

```bash
# install dependencies
yum install epel-release centos-release-scl
yum install http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-5.el7.nux.noarch.rpm
curl -o /etc/yum.repos.d/liquidsoap.repo \
  http://download.opensuse.org/repositories/home:/radiorabe:/liquidsoap/CentOS_7/home:radiorabe:liquidsoap.repo
# install airtime repo
curl -o /etc/yum.repos.d/airtime.repo \
  http://download.opensuse.org/repositories/home:/radiorabe:/airtime/CentOS_7/home:radiorabe:airtime.repo
yum install airtime-*
```

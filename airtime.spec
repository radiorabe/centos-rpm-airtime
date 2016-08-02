Name:           airtime
Version:        2.5.x
Release:        6%{?dist}
Summary:        radio rabe airtime installation

License:        AGPL
URL:            https://github.com/radiorabe/airtime
Source0:        https://github.com/radiorabe/airtime/archive/2.5.x.zip
Patch0:         media-monitor-disable-data_file.patch

BuildRequires: python-setuptools
BuildRequires: python-pip
BuildRequires: pytz
BuildRequires: python-mutagen
BuildRequires: python-amqp
BuildRequires: python-amqplib
BuildRequires: python-six
BuildRequires: python-configobj
BuildRequires: python-inotify
BuildRequires: python-pydispatcher
BuildRequires: python-poster
BuildRequires: python-kombu
BuildRequires: python-docopt
BuildRequires: python-mutagen
BuildRequires: python-vine

%description
RPM packaging for Radio Bern RaBe's CentOS-7 based installation
of Sourcefabric's Airtime Software.

%prep
%setup -q
%patch -P 0 -p 1

%build
ls -al


%install
rm -rf $RPM_BUILD_ROOT

# install airtime-web parts so apache finds them
mkdir -p $RPM_BUILD_ROOT/opt/rh/httpd24/root/var/www/
cp -rp airtime_mvc/* $RPM_BUILD_ROOT/opt/rh/httpd24/root/var/www/
ls $RPM_BUILD_ROOT/opt/rh/httpd24/root/var/www
mv $RPM_BUILD_ROOT/opt/rh/httpd24/root/var/www/public $RPM_BUILD_ROOT/opt/rh/httpd24/root/var/www/html

# install airtime-utils so they can be called by a user

mkdir -p $RPM_BUILD_ROOT/usr/{sbin,bin}
pushd utils
cp airtime-backup.py \
   airtime-log \
   airtime-log.php \
   airtime-silan \
   airtime-import/airtime-import \
   $RPM_BUILD_ROOT/usr/sbin/

cp airtime-test-soundcard \
   airtime-test-soundcard.py \
   airtime-test-stream \
   airtime-test-stream.py \
   $RPM_BUILD_ROOT/usr/bin/
popd

export PYTHONPATH=$RPM_BUILD_ROOT/${_prefix}usr/lib64/python2.7/site-packages
mkdir -p $RPM_BUILD_ROOT/${_prefix}usr/lib64/python2.7/site-packages

# install media-monitor python app
pushd python_apps/media-monitor/
python setup.py build
python setup.py install --prefix=$RPM_BUILD_ROOT/${_prefix}usr --install-lib=lib64
popd

# install std_err_override module
pushd python_apps/std_err_override/
python setup.py build
python setup.py install --prefix=$RPM_BUILD_ROOT/${_prefix}usr --install-lib=lib64
popd

# install api_clients module
pushd python_apps/api_clients/
python setup.py build
python setup.py install --prefix=$RPM_BUILD_ROOT/${_prefix}usr --install-lib=lib64
popd

# remove global python stuff
rm $PYTHONPATH/easy-install.pth \
   $PYTHONPATH/site.*


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc


%changelog

%package -n airtime-web
Summary: radio rabe airtime web interface installation

Requires: rh-php56-php
Requires: httpd24-httpd
Requires: liquidsoap

%description -n airtime-web
Installs the airtime web interface into http24/php56 using fpm.

%files -n airtime-web
/opt/rh/httpd24/root/var/www/
%config /opt/rh/httpd24/root/var/www/application/configs/application.ini

%package -n airtime-utils
Summary: radio rabe airtime utils installation

%description -n airtime-utils
Installs the various utils neeeded by airtime to d stuff on the cli.

%files -n airtime-utils
/usr/sbin/airtime-backup.py
/usr/sbin/airtime-log
/usr/sbin/airtime-log.php
/usr/sbin/airtime-silan
/usr/sbin/airtime-import
/usr/bin/airtime-test-*

%package -n airtime-media-monitor
Summary: radio rabe airtime media montitor installation

AutoReqProv: no

Requires: python
Requires: pytz
Requires: python-mutagen
Requires: python-amqp
Requires: python-amqplib
Requires: python-six
Requires: python-configobj
Requires: python-inotify
Requires: python-pydispatcher
Requires: python-poster
Requires: python-kombu
Requires: python-docopt
Requires: python-vine
Requires: airtime-std_err_override

%description -n airtime-media-monitor
airtime media-monitor imports uploaded files and watches directories

%files -n airtime-media-monitor
/usr/bin/airtime-media-monitor
/usr/lib64/python2.7/site-packages/airtime_media_monitor*


%package -n airtime-std_err_override
Summary: radio rabe airtime std_err_override installation

AutoReqProv: no

Requires: python

%description -n airtime-std_err_override
stderr overriding capabilities for airtime

%files -n airtime-std_err_override
/usr/lib64/python2.7/site-packages/std_err_override*

%package -n airtime-api_clients
Summary: radio rabe airtime python api clients

AutoReqProv: no

Requires: python

%description -n airtime-api_clients
airtime python api client library

%files -n airtime-api_clients
/usr/lib64/python2.7/site-packages/api_clients*

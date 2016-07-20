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

# install media-monitor python app
pushd python_apps/media-monitor/
# this is not called in a specfile :)
# python setup.py bdist_rpm
# lets do it using pip :)
#pip install --install-option="--prefix=$RPM_BUILD_ROOT/%{_prefix}"  .
# or even easy_install since pip goesn't on osb
export PYTHONPATH=$RPM_BUILD_ROOT/${_prefix}usr/lib/python2.7/site-packages
#mkdir -p $RPM_BUILD_ROOT/${_prefix}usr/lib/python2.7/site-packages
#easy_install --prefix $RPM_BUILD_ROOT/%{_prefix} .
# and now we try setup.py directly
python setup.py build
python setup.py install --prefix=$RPM_BUILD_ROOT/${_prefix}
popd

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

Requires: pytz
Requires: python-mutagen
Requires: python-amqp
Requires: python-amqplib
Requires: python-six
Requires: python-configobj
Requires: python-inotify

%description -n airtime-media-monitor
airtime media-monitor imports uploaded files and watches directories

%files -n airtime-media-monitor
/usr/bin/airtime-media-monitor
/usr/lib/python2.7/site-packages/PyDispatcher-2.0.5-py2.7.egg-info/
/usr/lib/python2.7/site-packages/airtime_media_monitor-1.0-py2.7.egg-info/
/usr/lib/python2.7/site-packages/amqp-1.0.13-py2.7.egg-info/
/usr/lib/python2.7/site-packages/amqp/
/usr/lib/python2.7/site-packages/argparse-1.4.0-py2.7.egg-info/
/usr/lib/python2.7/site-packages/argparse.*
/usr/lib/python2.7/site-packages/media_monitor/
/usr/lib/python2.7/site-packages/mm2/
/usr/lib/python2.7/site-packages/poster-0.8.1-py2.7.egg-info/
/usr/lib/python2.7/site-packages/poster/
/usr/lib/python2.7/site-packages/pydispatch/
/usr/lib/python2.7/site-packages/pyinotify-0.9.6-py2.7.egg-info/
/usr/lib/python2.7/site-packages/pyinotify.*
/usr/lib/python2.7/site-packages/tests/



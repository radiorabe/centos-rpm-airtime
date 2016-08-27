Name:           airtime
Version:        2.5.x
Release:        6%{?dist}
Summary:        radio rabe airtime installation

License:        AGPL
URL:            https://github.com/radiorabe/airtime
Source0:        https://github.com/radiorabe/airtime/archive/2.5.x.zip
Source1:        airtime-media-monitor.service
Source2:        airtime-pypo.service
Patch0:         media-monitor-centos-setup.patch
Patch1:         media-monitor-log-json-to-stdout.patch
Patch2:         media-monitor-fix-loading-files-with-encoded-filenames.patch
Patch3:         pypo-centos-setup.patch

BuildRequires: python-setuptools
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
BuildRequires: python-requests

%description
RPM packaging for Radio Bern RaBe's CentOS-7 based installation
of Sourcefabric's Airtime Software.

%prep
%setup -q
%patch0 -p 1
%patch1 -p 1
%patch2 -p 1
%patch3 -p 1

%build
ls -al


%install
rm -rf $RPM_BUILD_ROOT

# Install system directories
install -d %{buildroot}/%{_sysconfdir}/%{name}
install -d %{buildroot}/%{_sharedstatedir}/%{name}-pypo
install -d %{buildroot}/%{_exec_prefix}/lib/systemd/system/

# install airtime-web parts in the right location for the scl httpd24 package
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
mkdir -p $PYTHONPATH

# install media-monitor python app
pushd python_apps/media-monitor/
python setup.py build
python setup.py install --prefix=$RPM_BUILD_ROOT/${_prefix}usr --install-lib=$PYTHONPATH
mkdir -p $RPM_BUILD_ROOT/${_prefix}etc/airtime/
cp install/media_monitor_logging.cfg $RPM_BUILD_ROOT/${_prefix}etc/airtime/media_monitor_logging.cfg
popd
install -d %{buildroot}/%{_tmppath}/%{name}/media-monitor
install %{SOURCE1} %{buildroot}/%{_exec_prefix}/lib/systemd/system/

# install std_err_override module
pushd python_apps/std_err_override/
python setup.py build
python setup.py install --prefix=$RPM_BUILD_ROOT/${_prefix}usr --install-lib=$PYTHONPATH
mv $PYTHONPATH/std_err_override*egg/std_err_override $PYTHONPATH/std_err_override
popd

# install api_clients module
pushd python_apps/api_clients/
python setup.py build
python setup.py install --prefix=$RPM_BUILD_ROOT/${_prefix}usr --install-lib=$PYTHONPATH
mv $PYTHONPATH/api_clients*egg/api_clients $PYTHONPATH/api_clients
popd

# install pypo module
pushd python_apps/pypo/
python setup.py build
python setup.py install --prefix=$RPM_BUILD_ROOT/${_prefix}usr --install-lib=$PYTHONPATH
popd
install %{SOURCE2} %{buildroot}/%{_exec_prefix}/lib/systemd/system/

# install icecast xsl
pushd python_apps/icecast2
mkdir -p $RPM_BUILD_ROOT/${_prefix}usr/share/icecast/web
cp airtime-icecast-status.xsl $RPM_BUILD_ROOT/${_prefix}usr/share/icecast/web/airtime-icecast-status.xsl
popd

# remove global python stuff
rm $PYTHONPATH/easy-install.pth \
   $PYTHONPATH/site.*


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc README CREDITS LICENSE LICENSE_3RD_PARTY
%dir %{_sysconfdir}/%{name}
%dir %{_tmppath}/%{name}


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

Requires: %{name} = %{version}-%{release}
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
Requires: airtime-api_clients
Requires: lsof

%description -n airtime-media-monitor
airtime media-monitor imports uploaded files and watches directories


%pre -n airtime-media-monitor
getent group airtime-media-monitor >/dev/null || groupadd -r airtime-media-monitor
getent passwd airtime-media-monitor >/dev/null || \
    useradd -r -g airtime-media-monitor -d /var/tmp/airtime/media-monitor -m \
    -c "Airtime media monitor" airtime-media-monitor
exit 0


%files -n airtime-media-monitor
%dir %attr(-, airtime-media-monitor, airtime-media-monitor) %{_tmppath}/%{name}/media-monitor
%config /etc/airtime/media_monitor_logging.cfg
/usr/bin/airtime-media-monitor
/usr/lib64/python2.7/site-packages/airtime_media_monitor*
/usr/lib/systemd/system/airtime-media-monitor.service



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



%package -n airtime-pypo
Summary: radio rabe airtime pypo installation

AutoReqProv: no

Requires: python
Requires: python-requests
Requires: liquidsoap


%description -n airtime-pypo
Python Play-Out for airtime calls liquidsoap as defined in airtime.


%pre -n airtime-pypo
getent group airtime-pypo >/dev/null || groupadd -r airtime-pypo
getent passwd airtime-pypo >/dev/null || \
    useradd -r -g airtime-pypo -d /var/lib/airtime-pypo  -m \
    -c "Airtime pypo system user account" airtime-pypo
exit 0


%files -n airtime-pypo
%dir %attr(-, airtime-pypo, airtime-pypo) %{_sharedstatedir}/%{name}-pypo
/usr/lib/systemd/system/airtime-pypo.service
/usr/lib64/python2.7/site-packages/airtime_playout-1.0-py2.7.egg
/usr/bin/airtime-liquidsoap
/usr/bin/airtime-playout
/usr/bin/pyponotify



%package -n airtime-icecast
Summary: radio rabe airtime icecast xsl installation

AutoReqProv: no

Requires: icecast

%description -n airtime-icecast
Install airtimes xsl into icecast.

%files -n airtime-icecast
/usr/share/icecast/web/airtime-icecast-status.xsl

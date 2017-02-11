
# define the version of centos-rpm-airtime to build against (used as part of the packages release)
%define _release 1
# uncomment to hack on a branch of centos-rpm-airtime
#%define _release master

Name:           airtime
Version:        2.5.x.0.1.0
%if 0%{?opensuse_bs}
# <centos-rpm-airtime-version>.<rebuild-count>.rabe
Release:        %{_release}.<B_CNT>.rabe
%else
# same thing with build 0 for non obs packages
Release:        %{_release}.0.rabe
%endif
Summary:        radio rabe airtime installation

License:        AGPL
URL:            https://github.com/radiorabe/%{name}
Source0:        https://github.com/radiorabe/%{name}/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        centos-rpm-%{name}-%{release}
# uncomment to hack on a branch of centos-rpm-airtime
#Source1:        https://github.com/radiorabe/centos-rpm-%{name}/archive/%{_release}.tar.gz#/centos-rpm-%{name}-%{_release}.tar.gz

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
BuildRequires: systemd

%description
RPM packaging for Radio Bern RaBe's CentOS-7 based installation
of Sourcefabric's Airtime Software.

%prep
%setup -q
%setup -q -T -D -a 1 -c -n %{name}-%{version}

%build
ls -al


%install
rm -rf $RPM_BUILD_ROOT

# Install system directories
install -d %{buildroot}/%{_sysconfdir}/%{name}
install -d %{buildroot}/%{_unitdir}

# isntall all the systemd units from centos-rpm repo
install centos-rpm-%{name}-%{_release}/*.service %{buildroot}/%{_unitdir}
install centos-rpm-%{name}-%{_release}/*.timer %{buildroot}/%{_unitdir}

# install airtime-web parts in the right location for the httpd package
mkdir -p $RPM_BUILD_ROOT/var/www/
cp -rp airtime_mvc/* $RPM_BUILD_ROOT/var/www/
ls $RPM_BUILD_ROOT/var/www
mv $RPM_BUILD_ROOT/var/www/public $RPM_BUILD_ROOT/var/www/html
# configure zend config dep into scl php
install -d %{buildroot}/etc/php.d
cat << EOF > %{buildroot}/etc/php.d/50-upload_tmp_dir.ini
[main]
upload_tmp_dir=/tmp
EOF
cat << EOF > %{buildroot}/etc/php.d/50-upload_max_filesize.ini
upload_max_filesize=20M
post_max_size=20M
EOF

# setup apache
install -d %{buildroot}/etc/httpd/conf.d
cat << EOF > %{buildroot}/etc/httpd/conf.d/airtime-fallback.conf
<Directory "/var/www/html/">
    FallbackResource /index.php
</Directory>
EOF


# install airtime-utils so they can be called by a user

mkdir -p $RPM_BUILD_ROOT/usr/{sbin,bin}
pushd utils
cp airtime-backup.py \
   airtime-log \
   airtime-log.php \
   airtime-import/airtime-import \
   $RPM_BUILD_ROOT/usr/sbin/

cp airtime-test-soundcard \
   airtime-test-soundcard.py \
   airtime-test-stream \
   airtime-test-stream.py \
   $RPM_BUILD_ROOT/usr/bin/
popd

# install airtime-silan
mkdir -p $RPM_BUILD_ROOT/usr/bin
pushd utils
cp airtime-silan \
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

Requires: php
Requires: php-pdo
Requires: php-pgsql
Requires: php-bcmath
Requires: php-mbstring
Requires: php-fpm
Requires: php-ZendFramework-full
Requires: httpd
Requires: liquidsoap

%description -n airtime-web
Installs the airtime web interface into http24/php56 using fpm.

%files -n airtime-web
/var/www/
%config /var/www/application/configs/application.ini
%config /etc/php.d/*.ini
%config /etc/httpd/conf.d/airtime-fallback.conf

%package -n airtime-utils
Summary: radio rabe airtime utils installation

%description -n airtime-utils
Installs the various utils neeeded by airtime to d stuff on the cli.

%files -n airtime-utils
/usr/sbin/airtime-backup.py
/usr/sbin/airtime-log
/usr/sbin/airtime-log.php
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
%{?systemd_requires}

%description -n airtime-media-monitor
airtime media-monitor imports uploaded files and watches directories

%pre -n airtime-media-monitor
getent group airtime-media-monitor >/dev/null || groupadd -r airtime-media-monitor
getent passwd airtime-media-monitor >/dev/null || \
    useradd -r -g airtime-media-monitor -d /var/tmp/airtime/media-monitor -m \
    -c "Airtime media monitor" airtime-media-monitor
exit 0

%post -n airtime-media-monitor
%systemd_post airtime-media-monitor.service

%preun -n airtime-media-monitor
%systemd_preun airtime-media-monitor.service

%postun -n airtime-media-monitor
%systemd_postun airtime-media-monitor.service

%files -n airtime-media-monitor
%dir %attr(-, airtime-media-monitor, airtime-media-monitor) %{_tmppath}/%{name}/media-monitor
%config /etc/%{name}/media_monitor_logging.cfg
%attr(550, -, -) %{_unitdir}/airtime-media-monitor.service
%{_bindir}/airtime-media-monitor
%{_libdir}/python2.7/site-packages/airtime_media_monitor*



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
Requires: python-setuptools
Requires: pytz
Requires: python-inotify
Requires: python2-pydispatcher
Requires: python-poster
Requires: python-mutagen
Requires: python-kombu
Requires: python-amqplib
Requires: python-vine
Requires: airtime-api_clients
Requires: airtime-std_err_override
%{?systemd_requires}

%description -n airtime-pypo
Python Play-Out for airtime calls liquidsoap as defined in airtime.


%pre -n airtime-pypo
getent group airtime-pypo >/dev/null || groupadd -r airtime-pypo
getent passwd airtime-pypo >/dev/null || \
    useradd -r -g airtime-pypo -d /dev/null \
    -c "Airtime pypo playout server" airtime-pypo
exit 0

%post -n airtime-pypo
%systemd_post airtime-pypo.service

%preun -n airtime-pypo
%systemd_preun airtime-pypo.service

%postun -n airtime-pypo
%systemd_postun airtime-pypo.service


%files -n airtime-pypo
%attr(550, -, -) %{_unitdir}/airtime-pypo.service
%{_libdir}/python2.7/site-packages/airtime_playout-1.0-py2.7.egg
%{_bindir}/airtime-liquidsoap
%{_bindir}/airtime-playout
%{_bindir}/pyponotify



%package -n airtime-icecast
Summary: radio rabe airtime icecast xsl installation

AutoReqProv: no

Requires: icecast

%description -n airtime-icecast
Install airtimes xsl into icecast.

%files -n airtime-icecast
/usr/share/icecast/web/airtime-icecast-status.xsl

%package -n airtime-silan
Summary: radio rabe airtime-silan installation

AutoReqProv: no

Requires: silan
%{?systemd_requires}

%description -n airtime-silan
Airtime silan analyses file using silan and stores cue_in and cue_out information on the files. It is
usually run on the same machine as airtime-media-monitor and in fact used to be part of it's ingest
process not long ago.

%post -n airtime-silan
%systemd_post airtime-silan.timer

%preun -n airtime-silan
%systemd_preun airtime-silan.timer

%postun -n airtime-silan
%systemd_postun airtime-silan.timer

%files -n airtime-silan
/usr/bin/airtime-silan
%attr(550, -, -) %{_unitdir}/airtime-silan.service
%attr(550, -, -) %{_unitdir}/airtime-silan.timer


# If neither fedora nor rhel was defined, try to guess them from %%{dist}
%if !0%{?rhel} && !0%{?fedora}
%{expand:%(echo "%{?dist}" | \
  sed -ne 's/^\.el\([0-9]\+\).*/%%define rhel \1/p')}
%{expand:%(echo "%{?dist}" | \
  sed -ne 's/^\.fc\?\([0-9]\+\).*/%%define fedora \1/p')}
%endif

%if 0%{?fedora} >= 15  ||  0%{?rhel} >= 7
%define with_systemd 1
%else
%define with_systemd 0
%define _initdir  /etc/rc.d/init.d
%endif

Name:           novnc
Version:        0.3
Release:        9%{?dist}
Summary:        VNC client using HTML5 (Web Sockets, Canvas) with encryption support

License:        GPLv3
URL:            https://github.com/kanaka/noVNC
Source0:        https://github.com/downloads/kanaka/noVNC/noVNC-%{version}.tar.gz
Source1:        openstack-nova-novncproxy.service
Source2:        openstack-nova-novncproxy.init


Patch0:         novnc-0.3-nova-wsproxy.patch
Patch1:         novnc-0.3-manpage.patch
Patch2:         novnc-0.3-call-websockify.patch
BuildArch:      noarch
BuildRequires:  python2-devel

%description
Websocket implementation of VNC client


%package -n openstack-nova-novncproxy
Summary:        Proxy server for noVNC traffic over Websockets
Requires:       novnc
Requires:       python-nova
Requires:       python-websockify

%if %{with_systemd}
Requires(post): systemd-units
Requires(post): systemd-sysv
Requires(preun): systemd-units
Requires(postun): systemd-units
%else
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
%endif

%description -n openstack-nova-novncproxy
OpenStack Nova noVNC server that proxies VNC traffic over Websockets

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build


%install
mkdir -p %{buildroot}/%{_usr}/share/novnc/utils
install -m 444 *html %{buildroot}/%{_usr}/share/novnc
#provide an index file to prevent default directory browsing
install -m 444 vnc.html %{buildroot}/%{_usr}/share/novnc/index.html

mkdir -p %{buildroot}/%{_usr}/share/novnc/include/
install -m 444 include/*.*  %{buildroot}/%{_usr}/share/novnc/include
mkdir -p %{buildroot}/%{_usr}/share/novnc/images
install -m 444 images/*.*  %{buildroot}/%{_usr}/share/novnc/images

mkdir -p %{buildroot}/%{_bindir}
install utils/launch.sh  %{buildroot}/%{_bindir}/novnc_server

install utils/nova-novncproxy %{buildroot}/%{_bindir}

mkdir -p %{buildroot}%{_mandir}/man1/
install -m 444 docs/nova-novncproxy.1 %{buildroot}%{_mandir}/man1/
install -m 444 docs/novnc_server.1 %{buildroot}%{_mandir}/man1/

%if %{with_systemd}
mkdir -p %{buildroot}%{_unitdir}
install -p -D -m 444 %{SOURCE1} %{buildroot}%{_unitdir}
%else
mkdir -p %{buildroot}%{_initddir}
install -p -D -m 755 %{SOURCE2} %{buildroot}%{_initddir}/openstack-nova-novncproxy
%endif


%post -n openstack-nova-novncproxy
%if %{with_systemd}
%else
# This adds the proper /etc/rc*.d links for the script
/sbin/chkconfig --add openstack-nova-novncproxy
%endif

%preun -n openstack-nova-novncproxy
%if %{with_systemd}
%else
if [ $1 -eq 0 ] ; then
    /sbin/service openstack-nova-novncproxy stop >/dev/null 2>&1
    /sbin/chkconfig --del openstack-nova-novncproxy
fi
%endif


%files
%doc README.md LICENSE.txt

%dir %{_usr}/share/novnc
%{_usr}/share/novnc/*.*
%dir %{_usr}/share/novnc/include
%{_usr}/share/novnc/include/*
%dir %{_usr}/share/novnc/images
%{_usr}/share/novnc/images/*
%{_bindir}/novnc_server
%{_mandir}/man1/novnc_server.1*


%files -n openstack-nova-novncproxy
%{_bindir}/nova-novncproxy
%{_mandir}/man1/nova-novncproxy.1*
%if %{with_systemd}
%{_unitdir}/openstack-nova-novncproxy.service
%else
%{_initdir}/openstack-nova-novncproxy
%endif

%changelog
* Thu Jun 14 2012 Matthew Miller <mattdm@mattdm.org> - 0.3-9
- Remove a dependency for openstack-nova-novncproxy on numpy

* Wed Jun 13 2012 Alan Pevec <apevec@redhat.com> - 0.3-8
- Add a dependency for openstack-nova-novncproxy on python-nova

* Wed Jun 13 2012 Jose Castro Leon <jose.castro.leon@cern.ch> - 0.3-7
- Add a dependency for openstack-nova-novncproxy on novnc

* Mon Jun 11 2012 Adam Young <ayoung@redhat.com> - 0.3-6
- systemd initialization for Nova Proxy
- system V init script
- remove Flash binary supporting older browsers

* Tue Jun 8 2012 Adam Young <ayoung@redhat.com> - 0.3-3
- Added man pages
- novnc_server usese the websockify executable, not wsproxy.py

* Tue Jun 7 2012 Adam Young <ayoung@redhat.com> - 0.3-2
- Make Javascript files non-executable, as they are not script files
- Patch Nova noVNC proxy to use websockify directly

* Tue May 15 2012 Adam Young <ayoung@redhat.com> - 0.3-1
- Added in support for the Nova noVNC proxy
- Added files for the images and inclues subdirectories

* Thu May 10 2012 Adam Young <ayoung@redhat.com> - 0.2
- Initial RPM release.

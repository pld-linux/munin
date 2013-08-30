# TODO
# - R: perl* should be autogenerated?
# - add plugins-java package and proper BRs
#
# Condtional build:
%bcond_with	sybase		# add Sybase support to munin-node
#
%include	/usr/lib/rpm/macros.perl
Summary:	Munin - the Linpro RRD data agent
Summary(pl.UTF-8):	Munin - agent danych RRD Linpro
Name:		munin
Version:	2.0.17
Release:	5
License:	GPL
Group:		Applications/WWW
Source0:	http://downloads.sourceforge.net/munin/%{name}-%{version}.tar.gz
# Source0-md5:	80c8e6090963ad888e43b90c77f0a866
Source1:	%{name}-node.init
Source2:	%{name}.cron
Source3:	%{name}-apache.conf
Source4:	%{name}.logrotate
Source5:	%{name}-node.logrotate
Source6:	%{name}-lighttpd.conf
Source7:	%{name}.tmpfiles
Source8:	%{name}-httpd.conf
Source9:	%{name}-node.service
Source10:	%{name}-asyncd.service
Source11:	%{name}-asyncd.init
Patch0:		%{name}-Makefile.patch
Patch1:		%{name}-plugins.patch
Patch2:		%{name}-templatedir.patch
Patch3:		%{name}-separate-configs.patch
Patch4:		%{name}-timeout.patch
URL:		http://munin.sourceforge.net/
BuildRequires:	perl-Encode
BuildRequires:	perl-Net-SNMP
BuildRequires:	perl-devel
BuildRequires:	rpm-perlprov
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.671
BuildRequires:	which
Requires(triggerpostun):	sed >= 4.0
Requires:	%{name}-common = %{version}-%{release}
Requires:	fonts-TTF-DejaVu
Requires:	perl-Date-Manip
Requires:	perl-FCGI
Requires:	perl-HTML-Template
Requires:	perl-Net-Server
Requires:	rrdtool >= 1.3.0
Requires:	webapps
Requires:	webserver(alias)
Requires:	webserver(auth)
Requires:	webserver(cgi)
Requires:	webserver(expires)
Conflicts:	apache-base < 2.4.0-1
Conflicts:	logrotate < 3.8.0
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_noautoreq_perl	DBD::Pg

%define		_sysconfdir	/etc/%{name}
%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_appdir		%{_datadir}/%{_webapp}
%define		_htmldir	/var/lib/%{name}/html

%description
Munin, formerly known as The Linpro RRD server, queries a number of
nodes, and processes the data using RRDtool and presents it on web
pages.

%description -l pl.UTF-8
Munin, znany poprzednio jako serwer RRD Linpro, odpytuje wiele węzłów
i przetwarza dane przy użyciu RRDtoola, a następnie prezentuje je na
stronach WWW.

%package common
Summary:	Munin - the Linpro RRD data agent - common files
Summary(pl.UTF-8):	Munin - agent danych RRD Linpro - wspólne pliki
Group:		Daemons
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd

%description common
Munin, formerly known as The Linpro RRD server, queries a number of
nodes, and processes the data using RRDtool and presents it on web
pages.

%description common -l pl.UTF-8
Munin, znany poprzednio jako serwer RRD Linpro, odpytuje wiele węzłów
i przetwarza dane przy użyciu RRDtoola, a następnie prezentuje je na
stronach WWW.

%package node
Summary:	Linpro RRD data agent
Summary(pl.UTF-8):	Agent danych RRD Linpro
Group:		Daemons
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name}-common = %{version}-%{release}
Requires:	logtail
Requires:	logtool
#Requires:	perl-Config-General
Requires:	perl-Net-Netmask
Requires:	perl-Net-SNMP
Requires:	perl-Net-Server
Requires:	perl-libwww
Requires:	procps >= 2.0.7
Requires:	rc-scripts >= 0.4.0.15
Requires:	systemd-units >= 38
Requires:	sysstat
Suggests:	perl-DBD-Pg
Conflicts:	logrotate < 3.7-4

%description node
The Munin node package returns statistical data on the request of a
Munin server.

%description node -l pl.UTF-8
Pakiet Munin dla węzła zwraca dane statystyczne na żądanie serwera
Munin.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build
%{__make} -j1 build JCVALID=no

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d/init.d,cron.d,logrotate.d},%{_bindir},%{_sbindir}} \
	$RPM_BUILD_ROOT/var/log/archive/munin \
	$RPM_BUILD_ROOT%{_webapps}/%{_webapp} \
	$RPM_BUILD_ROOT/usr/lib/tmpfiles.d \
	$RPM_BUILD_ROOT%{systemdunitdir}

%{__make} -j1 install \
	JCVALID=no \
	CHOWN=/bin/true \
	DESTDIR=$RPM_BUILD_ROOT

# move asyncd daemon do sbin
%{__mv} $RPM_BUILD_ROOT{%{_datadir}/munin,%{_sbindir}}/munin-asyncd

install %{SOURCE11} $RPM_BUILD_ROOT/etc/rc.d/init.d/munin-asyncd
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/munin-node
install %{SOURCE2} $RPM_BUILD_ROOT/etc/cron.d/munin
install %{SOURCE4} $RPM_BUILD_ROOT/etc/logrotate.d/munin
install %{SOURCE5} $RPM_BUILD_ROOT/etc/logrotate.d/munin-node

install %{SOURCE3} $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/apache.conf
install %{SOURCE8} $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/httpd.conf
install %{SOURCE6} $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/lighttpd.conf

install %{SOURCE7} $RPM_BUILD_ROOT/usr/lib/tmpfiles.d/%{name}.conf

install %{SOURCE9} $RPM_BUILD_ROOT%{systemdunitdir}/munin-node.service
install %{SOURCE10} $RPM_BUILD_ROOT%{systemdunitdir}/munin-asyncd.service

install dists/tarball/plugins.conf $RPM_BUILD_ROOT%{_sysconfdir}
ln -sf %{_sysconfdir}/plugins.conf $RPM_BUILD_ROOT%{_sysconfdir}/plugin-conf.d/munin-node

for f in cgi-graph cgi-html graph html limits update ; do
	touch $RPM_BUILD_ROOT/var/log/munin/munin-$f.log
done

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache-base
%webapp_unregister httpd %{_webapp}

%triggerin -- lighttpd
%webapp_register lighttpd %{_webapp}

%triggerun -- lighttpd
%webapp_unregister lighttpd %{_webapp}

%triggerpostun -- munin < 1.3.4-5
# rescue app config
if [ -f /etc/munin/munin.conf.rpmsave ]; then
	mv -f %{_webapps}/%{_webapp}/munin.conf{,.rpmnew}
	mv -f /etc/munin/munin.conf.rpmsave %{_webapps}/%{_webapp}/munin.conf

	# fix paths in munin.conf
	sed -i -e 's|dbdir.*|dbdir	/var/lib/munin/db|' \
		-e 's|tmpldir.*|tmpldir	%{_webapps}/%{_webapp}/templates|' \
		%{_webapps}/%{_webapp}/munin.conf
fi
# move RRDs to new location
cd /var/lib/munin
for i in *; do
	case "$i" in
		db|html|plugin-state) ;;
		*) mv -f "$i" db/ ;;
	esac
done

%post
for f in cgi-graph cgi-html graph html limits update ; do
	touch /var/log/munin/munin-$f.log
	chmod 660 /var/log/munin/munin-$f.log
	chown munin:http /var/log/munin/munin-$f.log
done

%post node
if [ "$1" = "1" ] ; then
	/sbin/chkconfig --add munin-node
	%{_sbindir}/munin-node-configure --shell | sh
fi
%service munin-node restart "Munin Node agent"
%service munin-asyncd try-restart "Munin Asyncd agent"
%systemd_post munin-node.service
%systemd_service_restart munin-asyncd.service

%preun node
if [ "$1" = "0" ] ; then
	%service munin-asyncd stop
	%service munin-node stop
	/sbin/chkconfig --del munin-node
	/sbin/chkconfig --del munin-asyncd
fi
%systemd_preun munin-node.service munin-asyncd.service

%postun node
%systemd_reload

%triggerpostun node -- munin-node < 2.0.17-1
%systemd_trigger munin-node.service

%pre common
%groupadd -g 158 munin
%useradd -o -u 158 -s /bin/false -g munin -c "Munin Node agent" -d /var/lib/munin munin

%postun common
if [ "$1" = "0" ]; then
	%userremove munin
	%groupremove munin
fi

%files
%defattr(644,root,root,755)
%dir %attr(750,munin,http) %{_webapps}/%{_webapp}
%dir %attr(750,munin,http) %{_webapps}/%{_webapp}/munin-conf.d
%dir %{_webapps}/%{_webapp}/templates
%{_webapps}/%{_webapp}/templates/*.tmpl
%dir %{_webapps}/%{_webapp}/templates/static
%{_webapps}/%{_webapp}/templates/static/*.css
%{_webapps}/%{_webapp}/templates/static/*.html
%{_webapps}/%{_webapp}/templates/static/*.ico
%{_webapps}/%{_webapp}/templates/static/*.js
%{_webapps}/%{_webapp}/templates/static/*.png
%dir %{_webapps}/%{_webapp}/templates/partial
%{_webapps}/%{_webapp}/templates/partial/*.tmpl
%config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/munin.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/httpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/lighttpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/cron.d/munin
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/munin
%attr(755,root,root) %{_sbindir}/munin-cron
%attr(755,root,root) %{_datadir}/munin/munin-check
%attr(755,root,root) %{_datadir}/munin/munin-graph
%attr(755,root,root) %{_datadir}/munin/munin-html
%attr(755,root,root) %{_datadir}/munin/munin-limits
%attr(755,root,root) %{_datadir}/munin/munin-update
%attr(755,root,root) %{_datadir}/munin/munin-datafile2storable
%attr(755,root,root) %{_datadir}/munin/munin-storable2datafile
%attr(755,munin,root) %dir %{_datadir}/munin/cgi
%attr(755,munin,root) %{_datadir}/munin/cgi/munin-cgi-graph
%attr(755,munin,root) %{_datadir}/munin/cgi/munin-cgi-html
%attr(755,munin,root) %dir %{_htmldir}
%{perl_vendorlib}/Munin/Master
%{_mandir}/man3/Munin::Master*
%{_mandir}/man5/munin.conf*
%{_mandir}/man8/munin-check*
%{_mandir}/man8/munin-cron*
%{_mandir}/man8/munin-graph*
%{_mandir}/man8/munin-html*
%{_mandir}/man8/munin-limits*
%{_mandir}/man8/munin-update*
%{_mandir}/man8/munin.*
%attr(771,munin,munin) %dir /var/lib/munin/db
%attr(770,munin,http) %dir /var/lib/munin/db/cgi-tmp
%attr(660,munin,http) %ghost /var/log/munin/munin-cgi-graph.log
%attr(660,munin,http) %ghost /var/log/munin/munin-cgi-html.log
%attr(660,munin,http) %ghost /var/log/munin/munin-graph.log
%attr(660,munin,http) %ghost /var/log/munin/munin-html.log
%attr(660,munin,http) %ghost /var/log/munin/munin-limits.log
%attr(660,munin,http) %ghost /var/log/munin/munin-update.log

%files common
%defattr(644,root,root,755)
%doc README ChangeLog logo* Checklist
%dir %{_datadir}/munin
/usr/lib/tmpfiles.d/%{name}.conf
%attr(770,munin,http) %dir /var/log/munin
%attr(750,munin,http) %dir /var/log/archive/munin
%attr(771,munin,munin) %dir /var/lib/munin
%attr(770,munin,http) %dir /var/run/munin
%dir %{perl_vendorlib}/Munin
%{perl_vendorlib}/Munin/Common
%{_mandir}/man3/Munin::Common*

%files node
%defattr(644,root,root,755)
%dir %{_sysconfdir}
%dir %{_sysconfdir}/plugins
%dir %{_sysconfdir}/plugin-conf.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/munin-node.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/plugins.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/plugin-conf.d/munin-node
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/munin-node
%attr(754,root,root) /etc/rc.d/init.d/munin-asyncd
%attr(754,root,root) /etc/rc.d/init.d/munin-node
%{systemdunitdir}/munin-asyncd.service
%{systemdunitdir}/munin-node.service
%attr(755,root,root) %{_bindir}/munindoc
%attr(755,root,root) %{_sbindir}/munin-asyncd
%attr(755,root,root) %{_sbindir}/munin-node
%attr(755,root,root) %{_sbindir}/munin-node-configure
%attr(755,root,root) %{_sbindir}/munin-run
%attr(755,root,root) %{_sbindir}/munin-sched
%{perl_vendorlib}/Munin/Node
%{perl_vendorlib}/Munin/Plugin
%{perl_vendorlib}/Munin/Plugin.pm
%attr(755,root,root) %{_datadir}/munin/munin-async
%dir %{_datadir}/munin/plugins
%attr(755,root,root) %{_datadir}/munin/plugins/*
%if !%{with sybase}
%exclude %{_datadir}/munin/plugins/sybase_space
%endif
%dir %attr(770,munin,munin) /var/lib/munin/plugin-state
%dir %attr(770,munin,munin) /var/spool/munin
%{_mandir}/man1/munin-node*
%{_mandir}/man1/munin-run*
%{_mandir}/man1/munin-sched*
%{_mandir}/man1/munindoc*
%{_mandir}/man3/Munin::Node*
%{_mandir}/man3/Munin::Plugin*
%{_mandir}/man5/munin-node.conf*

#%files plugins-java
#%defattr(644,root,root,755)
#%{_datadir}/munin/munin-jmx-plugins.jar

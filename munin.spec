#
# Condtional build:
%bcond_with	sybase		# add Sybase support to munin-node
#
%include	/usr/lib/rpm/macros.perl
Summary:	Munin - the Linpro RRD data agent
Summary(pl):	Munin - agent danych RRD Linpro
Name:		munin
Version:	1.3.2
Release:	0.2
License:	GPL
Group:		Daemons
Source0:	http://dl.sourceforge.net/munin/%{name}_%{version}.tar.gz
# Source0-md5:	9eef4a53626cee0e088391c5deb8bd51
Source1:	%{name}-node.init
Source2:	%{name}.cron
Source3:	%{name}-Makefile.config
Patch0:		%{name}-Makefile.patch
URL:		http://munin.sourceforge.net/
BuildRequires:	htmldoc
BuildRequires:	html2text
BuildRequires:	perl-devel
Requires:	%{name}-common = %{version}-%{release}
Requires:	perl-Date-Manip
Requires:	perl-HTML-Template
Requires:	perl-Net-Server
Requires:	rrdtool
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Munin, formerly known as The Linpro RRD server, queries a number of
nodes, and processes the data using RRDtool and presents it on web
pages.

%description -l pl
Munin, znany poprzednio jako serwer RRD Linpro, odpytuje wiele wêz³ów
i przetwarza dane przy u¿yciu RRDtoola, a nastêpnie prezentuje je na
stronach WWW.

%package common
Summary:	Munin - the Linpro RRD data agent - common files
Summary(pl):	Munin - agent danych RRD Linpro - wspólne pliki
Group:		Daemons
Requires(pre):	/usr/bin/getgid
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel

%description common
Munin, formerly known as The Linpro RRD server, queries a number of
nodes, and processes the data using RRDtool and presents it on web
pages.

%description common -l pl
Munin, znany poprzednio jako serwer RRD Linpro, odpytuje wiele wêz³ów
i przetwarza dane przy u¿yciu RRDtoola, a nastêpnie prezentuje je na
stronach WWW.

%package node
Summary:	Linpro RRD data agent
Summary(pl):	Agent danych RRD Linpro
Group:		Daemons
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name}-common = %{version}-%{release}
#Requires:	perl-Config-General
Requires:	perl-Net-Server
Requires:	perl-Net-SNMP
Requires:	perl-libwww
Requires:	procps >= 2.0.7
Requires:	sysstat

%description node
The Munin node package returns statistical data on the request of a
Munin server.

%description node -l pl
Pakiet Munin dla wêz³a zwraca dane statystyczne na ¿±danie serwera
Munin.

%prep
%setup -q
%patch0 -p1
install -m644 %{SOURCE3} Makefile.config.pld

%build
%{__make} clean
%{__make} build \
	CONFIG=Makefile.config.pld

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,cron.d}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/munin/{plugins,plugin-conf.d}
install -d $RPM_BUILD_ROOT/var/{lib,log}/munin
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/html

%{__make} install \
	CONFIG=Makefile.config.pld \
	DOCDIR=$RPM_BUILD_ROOT%{_docdir}/munin \
	MANDIR=$RPM_BUILD_ROOT%{_mandir} \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/munin-node
install %{SOURCE2} $RPM_BUILD_ROOT/etc/cron.d/munin

install node/node.d/README README.plugins

install dists/tarball/plugins.conf $RPM_BUILD_ROOT%{_sysconfdir}/munin/
install dists/tarball/plugins.conf $RPM_BUILD_ROOT%{_sysconfdir}/munin/plugin-conf.d/munin-node

install server/munin-htaccess $RPM_BUILD_ROOT%{_datadir}/%{name}/html/.htaccess
install server/style.css $RPM_BUILD_ROOT%{_datadir}/%{name}/html

# A hack so rpm won't find deps on perl(DBD::Sybase)
%if %{without sybase}
chmod -x $RPM_BUILD_ROOT%{_datadir}/%{name}/plugins/sybase_space
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post node
if [ "$1" = "1" ] ; then
	/sbin/chkconfig --add munin-node
	%{_sbindir}/munin-node-configure --shell | sh
	echo "Run \"/etc/rc.d/init.d/munin-node start\" to start Munin Node agent." >&2
else
	if [ -f /var/lock/subsys/munin-node ]; then
		/etc/rc.d/init.d/munin-node restart >&2
	fi
fi

%preun node
if [ "$1" = "0" ] ; then
	if [ -f /var/lock/subsys/munin-node ]; then
		/etc/rc.d/init.d/munin-node stop >&2
	fi
	/sbin/chkconfig --del munin-node
fi

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
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/cron.d/munin
%dir %{_sysconfdir}/munin/templates
%{_sysconfdir}/munin/templates/*
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/munin/munin.conf
%attr(755,root,root) %{_sbindir}/munin-cron
%attr(755,root,root) %{_datadir}/munin/munin-graph
%attr(755,root,root) %{_datadir}/munin/munin-html
%attr(755,root,root) %{_datadir}/munin/munin-limits
%attr(755,root,root) %{_datadir}/munin/munin-update
%attr(755,munin,root) %dir %{_datadir}/munin/html
%attr(755,munin,root) %dir %{_datadir}/munin/html/cgi
%attr(644,munin,root) %{_datadir}/munin/html/.htaccess
%attr(644,munin,root) %{_datadir}/munin/html/style.css
%attr(755,munin,root) %{_datadir}/munin/html/cgi/munin-cgi-graph
%{perl_vendorlib}/Munin.pm
%{_mandir}/man8/munin-graph*
%{_mandir}/man8/munin-update*
%{_mandir}/man8/munin-limits*
%{_mandir}/man8/munin-html*
%{_mandir}/man8/munin-cron*
%{_mandir}/man5/munin.conf*

%files common
%defattr(644,root,root,755)
%doc README.api README.plugins ChangeLog
# %{_docdir}/munin/README.config
%doc build/doc/*.{html,pdf}
%dir %{_sysconfdir}/munin
%dir %{_datadir}/munin
%attr(750,munin,root) %dir /var/log/munin
%attr(770,munin,munin) %dir /var/lib/munin

%files node
%defattr(644,root,root,755)
%dir %{_sysconfdir}/munin/plugins
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/munin/munin-node.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/munin/plugins.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/munin/plugin-conf.d/munin-node
%attr(754,root,root) /etc/rc.d/init.d/munin-node
%attr(755,root,root) %{_sbindir}/munin-run
%attr(755,root,root) %{_sbindir}/munin-node
%attr(755,root,root) %{_sbindir}/munin-node-configure
%attr(755,root,root) %{_sbindir}/munin-node-configure-snmp
%dir %{_datadir}/munin/plugins
%attr(755,root,root) %{_datadir}/munin/plugins/*
%dir %attr(770,munin,munin) /var/lib/munin/plugin-state
%{_mandir}/man5/munin-node*
%{_mandir}/man8/munin-run*
%{_mandir}/man8/munin-node*

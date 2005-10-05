%include	/usr/lib/rpm/macros.perl
Summary:	Munin is the Linpro RRD data agent
Name:		munin
Version:	1.3.2
Release:	0.1
License:	GPL
Group:		Daemons
Source0:	http://dl.sourceforge.net/%{name}/%{name}_%{version}.tar.gz
# Source0-md5:	9eef4a53626cee0e088391c5deb8bd51
Source1:	%{name}-node.init
Source2:	%{name}.cron
URL:		http://munin.sourceforge.net/
BuildRequires:	perl-devel
Requires:	perl-HTML-Template
Requires:	perl-Net-Server
Requires:	rrdtool
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Munin, formerly known as The Linpro RRD server, queries a number of
nodes, and processes the data using RRDtool and presents it on web
pages.

%package node
Summary:	Linpro RRD data agent
Group:		Daemons
Requires:	perl-Net-Server
#Requires:	perl-Config-General
Requires:	procps >= 2.0.7
Requires:	sysstat
BuildArch:	noarch

%description node
The Munin node package returns statistical data on the request of a
Munin server.

%prep
%setup -q

%build

# htmldoc and html2text are not available for Red Hat. Quick hack with perl:
# Skip the PDFs.
perl -pi -e 's,htmldoc munin,cat munin, or s,html(2text|doc),# $&,' Makefile
perl -pi -e 's,\$\(INSTALL.+\.(pdf|txt) \$\(DOCDIR,# $&,' Makefile
%{__make} 	clean
%{__make} 	CONFIG=dists/redhat/Makefile.config \
	build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,cron.d}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/munin/{plugins,plugin-conf.d}
install -d $RPM_BUILD_ROOT/var/{lib,log}/munin

install -d $RPM_BUILD_ROOT/var/www/html/munin

## Node
%{__make} 	CONFIG=dists/redhat/Makefile.config \
	DOCDIR=$RPM_BUILD_ROOT%{_docdir}/munin \
	MANDIR=$RPM_BUILD_ROOT%{_mandir} \
	DESTDIR=$RPM_BUILD_ROOT \
    	install

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/munin-node
install %{SOURCE2} $RPM_BUILD_ROOT/etc/cron.d/munin

cp node/node.d/README README.plugins

install dists/tarball/plugins.conf $RPM_BUILD_ROOT%{_sysconfdir}/munin/
install dists/tarball/plugins.conf $RPM_BUILD_ROOT%{_sysconfdir}/munin/plugin-conf.d/munin-node

## Server

# cf=%{buildroot}/etc/munin/munin.conf; sed 's,/var/www/munin,/var/www/html/munin,g' < $cf > $cf.patch && mv $cf.patch $cf

install server/munin-htaccess $RPM_BUILD_ROOT/var/www/html/munin/.htaccess
install server/style.css $RPM_BUILD_ROOT/var/www/html/munin

%clean
rm -rf $RPM_BUILD_ROOT

%pre node
%groupadd -g 158 munin
%useradd -o -u 158 -s /bin/false -g munin -c "Munin Node agent" -d /var/lib/munin

%post node
if [ "$1" = "1" ] ; then
	/sbin/chkconfig --add munin-node
	%{_sbindir}/munin-node-configure --shell | sh
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

%postun node
if [ "$1" = "0" ]; then
	%userremove munin
	%groupremove munin
fi

%pre
%groupadd -g 158 munin
%useradd -o -u 158 -s /bin/false -g munin -c "Munin Node agent" -d /var/lib/munin

%postun
if [ "$1" = "0" ]; then
	%userremove munin
	%groupremove munin
fi

%files
%defattr(644,root,root,755)
%doc README.api README.plugins ChangeLog
# %{_docdir}/munin/README.config
%attr(755,root,root) %{_bindir}/munin-cron
%{_datadir}/munin/munin-graph
%{_datadir}/munin/munin-html
%{_datadir}/munin/munin-limits
%{_datadir}/munin/munin-update

%{perl_vendorlib}/Munin.pm
#%{perl_vendorarch}/RRDs.pm
#%dir %{perl_vendorarch}/auto/RRDs
#%{perl_vendorarch}/auto/RRDs/RRDs.bs
#%attr(755,root,root) %{perl_vendorarch}/auto/RRDs/RRDs.so
#%{_mandir}/man3/RRDp.3*
#%{_mandir}/man3/RRDs.3*

%dir %{_sysconfdir}/munin
%dir %{_sysconfdir}/munin/templates
%{_sysconfdir}/munin/templates/*
/etc/cron.d/munin
%config(noreplace) %{_sysconfdir}/munin/munin.conf

%attr(-, munin, root) %dir /var/lib/munin
%attr(-, munin, root) %dir /var/log/munin
%attr(-, munin, root) %dir /var/www/html/munin
%attr(-, munin, root) %dir /var/www/html/munin/cgi/cgi
%attr(-, munin, root) /var/www/html/munin/style.css
%attr(-, munin, root) %config /var/www/html/munin/.htaccess

%{_mandir}/man8/munin-graph*
%{_mandir}/man8/munin-update*
%{_mandir}/man8/munin-limits*
%{_mandir}/man8/munin-html*
%{_mandir}/man8/munin-cron*
%{_mandir}/man5/munin.conf*

%files node
%defattr(644,root,root,755)
%doc build/doc/*.html
%dir %{_sysconfdir}/munin
%dir %{_sysconfdir}/munin/plugins
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/munin/munin-node.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/munin/plugins.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/munin/plugin-conf.d/munin-node
%attr(754,root,root) /etc/rc.d/init.d/munin-node
%attr(755,root,root) %{_sbindir}/munin-run
%attr(755,root,root) %{_sbindir}/munin-node
%attr(755,root,root) %{_sbindir}/munin-node-configure
%attr(755,root,root) %{_sbindir}/munin-node-configure-snmp
%attr(-, munin, root) %dir /var/log/munin
%dir %{_datadir}/munin

%dir %attr(770, munin, munin) /var/lib/munin
%dir %attr(770, munin, munin) /var/lib/munin/plugin-state

%{_datadir}/munin/plugins/*

%{_mandir}/man5/munin-node*
%{_mandir}/man8/munin-run*
%{_mandir}/man8/munin-node*

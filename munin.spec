Summary:	Munin is the Linpro RRD data agent
Name:		munin
Version:	1.3.2
Release:	0.1
License:	GPL
Group:		Daemons
Source0:	http://dl.sourceforge.net/%{name}-%{version}.tar.gz
# Source0-md5:	9eef4a53626cee0e088391c5deb8bd51
URL:		http://munin.sourceforge.net/
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

## Node
rm -rf $RPM_BUILD_ROOT
%{__make} 	CONFIG=dists/redhat/Makefile.config \
	DOCDIR=$RPM_BUILD_ROOT%{_docdir}/munin \
	MANDIR=$RPM_BUILD_ROOT%{_mandir} \
	DESTDIR=$RPM_BUILD_ROOT \
    	install-node install-node-plugins install-doc install-man

install -d $RPM_BUILD_ROOT%{_sysconfdir}/init.d
install -d $RPM_BUILD_ROOT%{_sysconfdir}/munin/plugins
install -d $RPM_BUILD_ROOT%{_sysconfdir}/munin/plugin-conf.d
install -d $RPM_BUILD_ROOT/var/lib/munin
install -d $RPM_BUILD_ROOT/var/log/munin

#install -m 0755 node/redhat/munin-node %{buildroot}/etc/init.d/
install dists/redhat/munin-node.rc $RPM_BUILD_ROOT%{_sysconfdir}/init.d/munin-node
install dists/tarball/plugins.conf $RPM_BUILD_ROOT%{_sysconfdir}/munin/
install dists/tarball/plugins.conf $RPM_BUILD_ROOT%{_sysconfdir}/munin/plugin-conf.d/munin-node

chmod -x $RPM_BUILD_ROOT%{_datadir}/munin/plugins/sybase_space
## Server

%{__make} 	CONFIG=dists/redhat/Makefile.config \
	DESTDIR=$RPM_BUILD_ROOT \
	install-main

# cf=%{buildroot}/etc/munin/munin.conf; sed 's,/var/www/munin,/var/www/html/munin,g' < $cf > $cf.patch && mv $cf.patch $cf

install -d $RPM_BUILD_ROOT/var/www/html/munin
install -d $RPM_BUILD_ROOT/var/log/munin
install -d $RPM_BUILD_ROOT/etc/cron.d
# silly RPM triggers want to make debug enabled libraries.  let it try.
install -d $RPM_BUILD_ROOT%{_prefix}/lib/debug

install dists/redhat/munin.cron.d $RPM_BUILD_ROOT/etc/cron.d/munin
install server/munin-htaccess $RPM_BUILD_ROOT/var/www/html/munin/.htaccess
install server/style.css $RPM_BUILD_ROOT/var/www/html/munin

install ChangeLog $RPM_BUILD_ROOT%{_docdir}/munin/ChangeLog


%clean
rm -rf $RPM_BUILD_ROOT

%pre node
getent group munin >/dev/null || groupadd -r munin
getent passwd munin > /dev/null || useradd -r -d /var/lib/munin -g munin munin

%post node
chmod -R g+w /var/lib/munin/
if [ $1 = 1 ] ; then
	/sbin/chkconfig --add munin-node
	%{_sbindir}/munin-node-configure --shell | sh
fi
chown -R munin /var/lib/munin

%preun node
if [ $1 = 0 ] ; then
	/sbin/chkconfig --del munin-node
	rmdir /var/log/munin 2>/dev/null || echo " "
fi

%pre
getent group munin >/dev/null || groupadd -r munin
getent passwd munin > /dev/null || useradd -r -d /var/lib/munin -g munin munin

%post
chown -R munin /var/www/html/munin
chown -R munin /var/log/munin
chown -R munin /var/lib/munin

%postun
if [ $1 = 0 ] ; then
	userdel munin
fi

%files
%defattr(644,root,root,755)
%doc %{_docdir}/munin/README.api
#%doc %{_docdir}/munin/README.config
%doc %{_docdir}/munin/README.plugins
%doc %{_docdir}/munin/COPYING
%doc %{_docdir}/munin/ChangeLog
%attr(755,root,root) %{_bindir}/munin-cron
%{_datadir}/munin/munin-graph
%{_datadir}/munin/munin-html
%{_datadir}/munin/munin-limits
%{_datadir}/munin/munin-update
%{_libdir}/perl5/*perl/5.*/Munin.pm
%dir %{_sysconfdir}/munin/templates
%dir %{_sysconfdir}/munin
%{_sysconfdir}/munin/templates/*
/etc/cron.d/munin
%config(noreplace) %{_sysconfdir}/munin/munin.conf
%attr(-, munin, root) %dir /var/lib/munin
%attr(-, munin, root) %dir /var/log/munin
%attr(-, munin, root) %dir /var/www/html/munin
%attr(-, munin, root) %dir /var/www/html/munin/cgi/cgi
%attr(-, munin, root) /var/www/html/munin/style.css
%config /var/www/html/munin/.htaccess
%doc %{_mandir}/man8/munin-graph*
%doc %{_mandir}/man8/munin-update*
%doc %{_mandir}/man8/munin-limits*
%doc %{_mandir}/man8/munin-html*
%doc %{_mandir}/man8/munin-cron*
%doc %{_mandir}/man5/munin.conf*

%files node
%defattr(644,root,root,755)
%config(noreplace) %{_sysconfdir}/munin/munin-node.conf
%config(noreplace) %{_sysconfdir}/munin/plugin-conf.d/munin-node
%attr(754,root,root) %config /etc/rc.d/init.d/munin-node
%config(noreplace) %{_sysconfdir}/munin/plugins.conf
%attr(755,root,root) %{_sbindir}/munin-run
%attr(755,root,root) %{_sbindir}/munin-node
%attr(755,root,root) %{_sbindir}/munin-node-configure
%attr(755,root,root) %{_sbindir}/munin-node-configure-snmp
%dir /var/log/munin
%dir %{_datadir}/munin
%dir %{_sysconfdir}/munin/plugins
%dir %{_sysconfdir}/munin
%dir /var/lib/munin
%dir %attr(-, root, munin) /var/lib/munin/plugin-state
%{_datadir}/munin/plugins/*
%doc %{_docdir}/munin/COPYING
%doc %{_docdir}/munin/munin-doc.html
%doc %{_docdir}/munin/munin-faq.html
%doc %{_mandir}/man8/munin-run*
%doc %{_mandir}/man8/munin-node*
%doc %{_mandir}/man5/munin-node*
#%doc %{_mandir}/man5/node.conf*

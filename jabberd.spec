# TODO: oracle/oci bcond
#
# Conditional build
%bcond_without	db	# db storage and authreg backends
%bcond_without	ldap	# ldap authreg backend
%bcond_without	mysql	# MySQL storage and authreg backends
%bcond_without	pgsql	# PostgreSQL storage and authreg backends
%bcond_without	sqlite	# SQLite v3 storage backend
# allows limiting the number of offline messages stored per user (mysql storage)
# and allows offline storage (queuing) of subscription requests and/or messages
# to be disabled
%bcond_with	bxmpp	# - patches c2s to allow connections from Flash clients which don't use proper XMPP

%define		skip_post_check_so	mod_.*.so.0.0.0 libstorage.so.0.0.0

Summary:	Jabber/XMPP server
Summary(pl.UTF-8):	Serwer Jabber/XMPP
Name:		jabberd
Version:	2.7.0
Release:	1
License:	GPL v2+
Group:		Applications/Communications
Source0:	https://github.com/jabberd2/jabberd2/releases/download/jabberd-%{version}/%{name}-%{version}.tar.xz
# Source0-md5:	39b4b5286a1ad91ff84c3588fa26efa8
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-perlscript.patch
Patch1:		%{name}-daemonize.patch
Patch2:		%{name}-default_config.patch
Patch4:		%{name}-delay_jobs.patch
Patch5:		%{name}-binary_path.patch
#bcond bxmpp
Patch22:	http://www.marquard.net/jabber/patches/patch-flash-v2
URL:		http://jabberd2.org/
BuildRequires:	autoconf >= 2.61
BuildRequires:	autoconf-archive
BuildRequires:	automake >= 1:1.11
%{?with_db:BuildRequires:	db-devel >= 4.1.24}
BuildRequires:	expat-devel
BuildRequires:	gettext-tools
BuildRequires:	gsasl-devel >= 1.4.0
BuildRequires:	libidn-devel >= 0.3.0
BuildRequires:	libstdc++-devel
BuildRequires:	libtool
%{?with_mysql:BuildRequires:	mysql-devel >= 5}
%{?with_ldap:BuildRequires:	openldap-devel >= 2.1.0}
BuildRequires:	openssl-devel >= 1.0.2
BuildRequires:	pam-devel
%{?with_pgsql:BuildRequires:	postgresql-devel >= 8}
BuildRequires:	rpm-perlprov >= 3.0.3-16
BuildRequires:	rpmbuild(macros) >= 1.268
%{?with_sqlite:BuildRequires:	sqlite3-devel >= 3}
BuildRequires:	udns-devel
BuildRequires:	zlib-devel
Requires(post):	sed >= 4.0
Requires(post):	textutils
Requires(post,preun):	/sbin/chkconfig
Requires:	gsasl >= 1.4.0
Requires:	jabber-common
Requires:	libidn >= 0.3.0
Requires:	openssl >= 1.0.2
Requires:	rc-scripts
Suggests:	cyrus-sasl-digest-md5
Suggests:	cyrus-sasl-plain
Obsoletes:	jabber < 2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Modern open source Jabber server, implementing latest XMPP protocol.

%description -l pl.UTF-8
Nowoczesny, wolnodostępny serwer Jabbera implementujący najnowszy
protokół XMPP.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch4 -p1
%patch5 -p1

%if %{with bxmpp}
%patch22 -p0
%endif

%build
#http://j2.openaether.org/bugzilla/show_bug.cgi?id=17
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--bindir="%{_libdir}/%{name}" \
	--sysconfdir="%{_sysconfdir}/jabber" \
	%{?with_db:--enable-db} \
	%{?with_mysql:--enable-mysql} \
	%{?with_pgsql:--enable-pgsql} \
	--enable-fs \
	--enable-anon \
	--enable-pipe \
	--enable-pam \
	%{?with_ldap:--enable-ldap} \
	%{?with_sqlite:--enable-sqlite} \
	%{?debug:--enable-debug} \
	--disable-silent-rules

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},/var/lib/%{name}/{db,stats},/etc/{sysconfig,rc.d/init.d}}
install -d $RPM_BUILD_ROOT%{systemdunitdir}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%{__mv} $RPM_BUILD_ROOT%{_libdir}/jabberd/jabberd $RPM_BUILD_ROOT%{_sbindir}
%{__mv} $RPM_BUILD_ROOT/usr/lib/systemd/system/* $RPM_BUILD_ROOT%{systemdunitdir}
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/jabber{,/templates}/*.dist 

# drop Upstart configuration files
%{__rm} -f $RPM_BUILD_ROOT%{_sysconfdir}/jabber/*.conf 
%{__rm} -f $RPM_BUILD_ROOT%{_prefix}/etc/init/*.conf

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f %{_sysconfdir}/jabber/secret ] ; then
	SECRET=`cat %{_sysconfdir}/jabber/secret`
	if [ -n "$SECRET" ] ; then
		echo "Updating component authentication secret in Jabberd config files..."
		%{__sed} -i -e "s/>secret</>$SECRET</" %{_sysconfdir}/jabber/*.xml
	fi
fi

/sbin/chkconfig --add jabberd
%service jabberd restart "Jabber server"
%systemd_post jabberd.service

%if %{with avatars}
echo "This j2 package has new functionality, please read AVATARS file."
%endif

%preun
if [ "$1" = "0" ]; then
	%service jabberd stop
	/sbin/chkconfig --del jabberd
fi
%systemd_preun jabberd.service

%postun
%systemd_reload

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS README TODO
%doc tools/{%{?with_mysql:db-*.mysql,}%{?with_pgsql:db-*.pgsql,}%{?with_sqlite:db-*.sqlite,}pipe-auth.pl}
%attr(640,root,jabber) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/jabber/*.cfg
%attr(640,root,jabber) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/jabber/*.xml
%dir %{_sysconfdir}/jabber/templates
%attr(640,root,jabber) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/jabber/templates/*.xml
%attr(755,root,root) %{_sbindir}/jabberd
%dir %{_libdir}/jabberd
%attr(755,root,root) %{_libdir}/%{name}/c2s
%attr(755,root,root) %{_libdir}/%{name}/router
%attr(755,root,root) %{_libdir}/%{name}/s2s
%attr(755,root,root) %{_libdir}/%{name}/sm
%attr(755,root,root) %{_libdir}/%{name}/libstorage.so*
%attr(755,root,root) %{_libdir}/%{name}/authreg_*.so*
%attr(755,root,root) %{_libdir}/%{name}/mod_*.so*
%attr(755,root,root) %{_libdir}/%{name}/storage_*.so*
# XXX: are these needed?
%{_libdir}/%{name}/*.la
%dir %attr(770,root,jabber) /var/lib/%{name}
%dir %attr(770,root,jabber) /var/lib/%{name}/db
%dir %attr(770,root,jabber) /var/lib/%{name}/stats
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%{_mandir}/man8/c2s.8*
%{_mandir}/man8/jabberd.8*
%{_mandir}/man8/router.8*
%{_mandir}/man8/s2s.8*
%{_mandir}/man8/sm.8*
%{systemdunitdir}/jabberd-c2s.service
%{systemdunitdir}/jabberd-router.service
%{systemdunitdir}/jabberd-s2s.service
%{systemdunitdir}/jabberd-sm.service
%{systemdunitdir}/jabberd.service

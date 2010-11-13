#
# Conditional build
%bcond_without	db	# don't build db storage and authreg backends
%bcond_without	ldap	# don't build ldap authreg backend
%bcond_without	mysql	# don't build MySQL storage and authreg backends
%bcond_without	pgsql	# don't build PostgreSQL storage and authreg backends
%bcond_without	sqlite	# don't build SQLite v3 storage backend
# allows limiting the number of offline messages stored per user (mysql storage)
# and allows offline storage (queuing) of subscription requests and/or messages
# to be disabled
%bcond_with	bxmpp	# - patches c2s to allow connections from Flash clients which don't use proper XMPP

%include	/usr/lib/rpm/macros.perl
Summary:	Jabber/XMPP server
Summary(pl.UTF-8):	Serwer Jabber/XMPP
Name:		jabberd
Version:	2.2.9
Release:	2
License:	GPL
Group:		Applications/Communications
Source0:	http://ftp.xiaoka.com/jabberd2/releases/%{name}-%{version}.tar.bz2
# Source0-md5:	bfc0fa473c2a453fcbba4f95f28c5d70
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	db-setup.sqlite
Patch0:		%{name}-perlscript.patch
Patch1:		%{name}-daemonize.patch
Patch2:		%{name}-default_config.patch
Patch4:		%{name}-delay_jobs.patch
Patch5:		%{name}-binary_path.patch
Patch6:		%{name}-reconnect.patch
#bcond bxmpp
Patch22:	http://www.marquard.net/jabber/patches/patch-flash-v2
URL:		http://jabberd.jabberstudio.org/
BuildRequires:	autoconf
BuildRequires:	automake
%{?with_db:BuildRequires:	db-devel >= 4.1.24}
BuildRequires:	expat-devel
BuildRequires:	gettext-devel
BuildRequires:	gsasl-devel >= 0.2.28
BuildRequires:	libidn-devel >= 0.3.0
BuildRequires:	libstdc++-devel
BuildRequires:	libtool
%{?with_mysql:BuildRequires:	mysql-devel}
%{?with_ldap:BuildRequires:	openldap-devel}
BuildRequires:	openssl-devel >= 0.9.6d
BuildRequires:	pam-devel
%{?with_pgsql:BuildRequires:	postgresql-devel}
BuildRequires:	rpm-perlprov >= 3.0.3-16
BuildRequires:	rpmbuild(macros) >= 1.268
%{?with_sqlite:BuildRequires:	sqlite3-devel}
BuildRequires:	udns-devel
Requires(post):	sed >= 4.0
Requires(post):	textutils
Requires(post,preun):	/sbin/chkconfig
Requires:	jabber-common
Requires:	rc-scripts
Obsoletes:	jabber
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
%patch6 -p1

%if %{with bxmpp}
%patch22 -p0
%endif

install %{SOURCE3} tools/

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
	%{?debug:--enable-debug}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},/var/lib/%{name}/{db,stats},/var/run/jabber,/etc/{sysconfig,rc.d/init.d}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

mv $RPM_BUILD_ROOT%{_libdir}/jabberd/jabberd $RPM_BUILD_ROOT%{_sbindir}
rm $RPM_BUILD_ROOT%{_sysconfdir}/jabber{,/templates}/*.dist

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

%if %{with avatars}
echo "This j2 package has new functionality, please read AVATARS file."
%endif

%preun
if [ "$1" = "0" ]; then
	%service jabberd stop
	/sbin/chkconfig --del jabberd
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS README TODO
%doc tools/{migrate.pl,db-setup.mysql,db-setup.pgsql,%{?with_sqlite:db-setup.sqlite,}pipe-auth.pl}
%attr(640,root,jabber) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/jabber/*.cfg
%attr(640,root,jabber) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/jabber/*.xml
%dir %{_sysconfdir}/jabber/templates
%attr(640,root,jabber) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/jabber/templates/*.xml
%attr(755,root,root) %{_sbindir}/*
%dir %{_libdir}/jabberd
%attr(755,root,root) %{_libdir}/%{name}/*
%dir %attr(770,root,jabber) /var/lib/%{name}
%dir %attr(770,root,jabber) /var/lib/%{name}/db
%dir %attr(770,root,jabber) /var/lib/%{name}/stats
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%{_mandir}/man*/*

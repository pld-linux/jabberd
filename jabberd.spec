#
# TODO:
# add bcond avatars with avatars patch, this feature will be released
# at jabberd-2.1
#
# Conditional build
%bcond_without	db	# - don't build db storage and authreg backends
%bcond_without	pgsql	# - don't build PostgreSQL storage and authreg backends
%bcond_without	mysql	# - don't build MySQL storage and authreg backends
%bcond_without	ldap	# - don't build ldap authreg backend
%bcond_without  sqlite	# - don't build SQLite v3 storage and authreg backends
%bcond_without	oq
# allows limiting the number of offline messages stored per user (mysql storage)
# and allows offline storage (queuing) of subscription requests and/or messages
# to be disabled
%bcond_with	amp	# - Advanced Message Processing (JEP-0079) implementation
%bcond_with	bxmpp	# - patches c2s to allow connections from Flash clients which don't use proper XMPP

%include	/usr/lib/rpm/macros.perl
Summary:	Jabber/XMPP server
Summary(pl):	Serwer Jabber/XMPP
Name:		jabberd
Version:	2.0s6
Release:	8
License:	GPL
Group:		Applications/Communications
Source0:	http://www.jabberstudio.org/files/jabberd2/%{name}-%{version}.tar.gz
# Source0-md5:	ca2818885e126181e002949c71603df3
Source1:	%{name}.init
Source2:	%{name}.sysconfig
#bcond amp
Source3:	http://svn.cmeerw.net/src/jabberd2/sqlite/tools/db-setup.sqlite
Source4:	http://svn.cmeerw.net/src/jabberd2/sqlite/sm/storage_sqlite.c
Source5:	http://neonux.org/jabberd2/mod_amp.c
Patch0:		%{name}-perlscript.patch
Patch1:		%{name}-daemonize.patch
Patch2:		%{name}-default_config.patch
Patch3:		%{name}-sysconfdir.patch
Patch4:		%{name}-delay_jobs.patch
Patch5:		%{name}-binary_path.patch
Patch6:		http://svn.cmeerw.net/src/jabberd2/sqlite/%{name}-2.0-sqlite.diff
Patch7:		%{name}-sm-examples.patch
# Feature release :)
Patch8:		http://www.marquard.net/jabber/patches/patch-zzzz-s2s-v5
Patch9:		http://www.marquard.net/jabber/patches/patch-s2-config-update
Patch10:	http://www.marquard.net/jabber/patches/patch-sm-shutdown
Patch11:	http://www.marquard.net/jabber/patches/patch-reconnect
Patch12:	http://www.marquard.net/jabber/patches/patch-db-cleanup
Patch13:	http://www.marquard.net/jabber/patches/patch-sm-db-fixup
Patch14:	http://www.marquard.net/jabber/patches/patch-empty-jid-v2
Patch15:	http://www.marquard.net/jabber/patches/patch-mod_session
Patch16:	http://www.marquard.net/jabber/patches/patch-zzzzz-s2s-85
Patch17:	http://www.marquard.net/jabber/patches/patch-zzzzz-s2s-86
Patch18:	http://www.marquard.net/jabber/patches/patch-sx-stream-err
Patch19:	http://www.marquard.net/jabber/patches/patch-zzzzz-s2s-88
#bcond amp
#original patch from http://neonux.org/jabberd2/mod_amp.patch
Patch20:	%{name}-mod_amp.patch
#bcond oq
Patch21:	http://www.marquard.net/jabber/patches/patch-sm-offline-quota
#bcond bxmpp
Patch22:	http://www.marquard.net/jabber/patches/patch-flash-v2
# Feature release :)
Patch23:	http://www.marquard.net/jabber/patches/patch-doc-updates
Patch24:	http://www.marquard.net/jabber/patches/patch-ldap-referral
# avatars
#http://j2.openaether.org/bugzilla/attachment.cgi?id=23&action=diff&context=patch&collapsed=&headers=1&format=raw
Patch25:	%{name}-mod_iq_vcard.patch
Patch26:	%{name}-avatars.patch
URL:		http://jabberd.jabberstudio.org/
BuildRequires:	autoconf
BuildRequires:	automake
%{?with_db:BuildRequires:	db-devel >= 4.1.24}
BuildRequires:	gettext-devel
BuildRequires:	libidn-devel >= 0.3.0
BuildRequires:	libtool
%{?with_mysql:BuildRequires:	mysql-devel}
%{?with_ldap:BuildRequires:	openldap-devel >= 2.1.0}
BuildRequires:	openssl-devel >= 0.9.6d
BuildRequires:	pam-devel
%{?with_pgsql:BuildRequires:	postgresql-devel}
%{?with_sqlite:BuildRequires:	sqlite3-devel}
BuildRequires:	rpm-perlprov >= 3.0.3-16
PreReq:		rc-scripts
PreReq:		jabber-common
Requires(post):	textutils
Requires(post):	/usr/bin/perl
Requires(post,preun):	/sbin/chkconfig
Requires:	jabber-common
Obsoletes:	jabber
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Modern open source Jabber server, implementing latest XMPP protocol.

%description -l pl
Nowoczesny, wolnodostêpny serwer Jabbera implementuj±cy najnowszy
protokó³ XMPP.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
#SQLite
%if %{with sqlite}
%patch6 -p1
%patch7 -p1
install %{SOURCE3} tools/
install %{SOURCE4} sm/
%endif
#
%patch8 -p0
%patch9 -p0
%patch10 -p0
%patch11 -p0
%patch12 -p0
%patch13 -p0
%patch14 -p0
%patch15 -p0
%patch16 -p0
%patch17 -p0
%patch18 -p0
%patch19 -p0

%if %{with amp}
install %{SOURCE5} sm/
%patch20 -p1
%endif

%if %{with oq}
%patch21 -p0
%endif

%if %{with bxmpp}
%patch22 -p0
%endif
%patch23 -p0
%patch24 -p0
%patch25 -p1
%patch26 -p1

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--bindir="%{_libdir}/%{name}" \
	%{?with_db:--enable-db} \
	%{!?with_mysql:--disable-mysql} \
	%{?with_pgsql:--enable-pgsql} \
	--enable-fs \
	--enable-anon \
	--enable-pipe \
	--enable-pam \
	%{?with_ldap:--enable-ldap} \
	%{?with_mysql:--enable-sqlite} \
	%{?debug:--enable-debug}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},/var/lib/%{name}/db,/var/run/jabber,/etc/{sysconfig,rc.d/init.d}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

mv $RPM_BUILD_ROOT%{_libdir}/jabberd/jabberd $RPM_BUILD_ROOT%{_sbindir}
rm $RPM_BUILD_ROOT%{_sysconfdir}/jabber{,/templates}/*.dist

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f /etc/jabber/secret ] ; then
	SECRET=`cat /etc/jabber/secret`
	if [ -n "$SECRET" ] ; then
		echo "Updating component authentication secret in Jabberd config files..."
		perl -pi -e "s/>secret</>$SECRET</" /etc/jabber/*.xml
	fi
fi

/sbin/chkconfig --add jabberd
if [ -r /var/lock/subsys/jabberd ]; then
	/etc/rc.d/init.d/jabberd restart >&2
else
	echo "Run \"/etc/rc.d/init.d/jabberd start\" to start Jabber server."
fi

echo "This j2 package has new functionality, please read AVATARS file."

%preun
if [ "$1" = "0" ]; then
	if [ -r /var/lock/subsys/jabberd ]; then
		/etc/rc.d/init.d/jabberd stop >&2
	fi
	/sbin/chkconfig --del jabberd
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS PROTOCOL README TODO AVATARS
%doc tools/{migrate.pl,db-setup.mysql,db-setup.pgsql,db-setup.sqlite,pipe-auth.pl}
%attr(640,root,jabber) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/jabber/*.cfg
%attr(640,root,jabber) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/jabber/*.xml
%dir %{_sysconfdir}/jabber/templates
%attr(640,root,jabber) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/jabber/templates/*.xml
%attr(755,root,root) %{_sbindir}/*
%dir %{_libdir}/jabberd
%attr(755,root,root) %{_libdir}/%{name}/*
%dir %attr(770,root,jabber) /var/lib/%{name}
%dir %attr(770,root,jabber) /var/lib/%{name}/db
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%{_mandir}/man*/*

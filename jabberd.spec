%include	/usr/lib/rpm/macros.perl
#
# Conditional build:
# _without_db		- don't build db storage and authreg backends
# _without_pgsql	- don't build pgsql storage and authreg backends
# _without_mysql	- don't build mysql storage and authreg backends
# _without_ldap		- don't build ldap authreg backend
#
Summary:	Jabber/XMPP server
Summary(pl):	Serwer Jabber/XMPP
Name:		jabberd
Version:	2.0
Release:	0.b1.2
License:	GPL
Group:		Applications/Communications
Source0:	http://www.jabberstudio.org/files/jabberd2/%{name}-%{version}b1.tar.gz
# Source0-md5:	845d023346743b997201873d938fb8f7
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-perlscript.patch
Patch1:		%{name}-binary_path.patch
Patch2:		%{name}-daemonize.patch
Patch3:		%{name}-default_config.patch
Patch4:		%{name}-sysconfdir.patch
Patch5:		%{name}-delay_jobs.patch
Patch6:		%{name}-c2s_crash.patch
Patch7:		%{name}-digest_md5_rspauth.patch
URL:		http://jabberd.jabberstudio.org
BuildRequires:	openssl-devel >= 0.9.6b
%{!?_without_db:BuildRequires:	db-devel >= 4.1.24}
%{!?_without_mysql:BuildRequires:       mysql-devel}
%{!?_without_ldap:BuildRequires:	openldap-devel >= 2.1.0}
%{!?_without_pgsql:BuildRequires:	postgresql-devel}
BuildRequires:	pam-devel
BuildRequires:	rpm-perlprov >= 3.0.3-16
BuildRequires:	gettext-devel
PreReq:		rc-scripts
Requires(pre):	/usr/bin/getgid
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post): jabber-common
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
%setup -q -n %{name}-%{version}b1
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--bindir="%{_libdir}/%{name}" \
	--enable-authreg="anon pipe pam
		%{!?_without_db:db}
		%{!?_without_ldap:ldap}
		%{!?_without_mysql:mysql}
		%{!?_without_pgsql:pgsql}" \
	--enable-storage="fs
		%{!?_without_db:db}
		%{!?_without_mysql:mysql}
		%{!?_without_pgsql:pgsql}" \
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

%pre
if [ "$1" = "1" ] ; then
	if [ ! -n "`getgid jabber`" ]; then
		/usr/sbin/groupadd -f -g 74 jabber
	fi
	if [ ! -n "`id -u jabber 2>/dev/null`" ]; then
		/usr/sbin/useradd -g jabber -d /var/lib/jabber -u 74 -s /bin/false jabber 2>/dev/null
	fi
fi

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

%preun
if [ "$1" = "0" ]; then
	if [ -r /var/lock/subsys/jabberd ]; then
		/etc/rc.d/init.d/jabberd stop >&2
	fi
	/sbin/chkconfig --del jabberd
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog INSTALL NEWS README TODO tools/db-setup.mysql tools/db-setup.pgsql tools/pipe-auth.pl
%attr(640,root,jabber) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/jabber/*.cfg
%attr(640,root,jabber) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/jabber/*.xml
%dir %{_sysconfdir}/jabber/templates
%attr(640,root,jabber) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/jabber/templates/*.xml
%attr(755,root,root) %{_sbindir}/*
%dir %{_libdir}/jabberd
%attr(755,root,root) %{_libdir}/%{name}/*
%dir %attr(770,root,jabber) /var/lib/%{name}
%dir %attr(770,root,jabber) /var/lib/%{name}/db
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(640,root,root) %config(noreplace) %verify(not md5 size mtime) /etc/sysconfig/%{name}
%{_mandir}/man*/*

#
# Conditional build
%bcond_without	db	# - don't build db storage and authreg backends
%bcond_without	pgsql	# - don't build pgsql storage and authreg backends
%bcond_without	mysql	# - don't build mysql storage and authreg backends
%bcond_without	ldap	# - don't build ldap authreg backend
#
%include	/usr/lib/rpm/macros.perl
Summary:	Jabber/XMPP server
Summary(pl):	Serwer Jabber/XMPP
Name:		jabberd
Version:	2.0s3
Release:	2
License:	GPL
Group:		Applications/Communications
Source0:	http://www.jabberstudio.org/files/jabberd2/%{name}-%{version}.tar.gz
# Source0-md5:	c15f8f07cb2ee499cd21c0b883b9f353
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-perlscript.patch
Patch1:		%{name}-daemonize.patch
Patch2:		%{name}-default_config.patch
Patch3:		%{name}-sysconfdir.patch
Patch4:		%{name}-delay_jobs.patch
Patch5:		%{name}-binary_path.patch

Patch6:		%{name}-nad-cache.patch
Patch7:		%{name}-patch-sm.patch
Patch8:		%{name}-patch-sm-mod_announce.patch
Patch9:		%{name}-patch-io.patch
Patch10:	%{name}-patch-sm-pkt.patch
Patch11:	%{name}-patch-pool-cleanup.patch
Patch12:	%{name}-patch-ssl.patch
Patch13:	%{name}-patch-s2s-main.patch
Patch14:	%{name}-patch-util-xhash.patch
Patch15:	%{name}-patch-scod-mech_plain.patch
Patch16:	%{name}-util-nad.patch

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
BuildRequires:	rpm-perlprov >= 3.0.3-16
PreReq:		rc-scripts
#Requires(pre):	/usr/bin/getgid
#Requires(pre):	/bin/id
#Requires(pre):	/usr/sbin/groupadd
#Requires(pre):	/usr/sbin/useradd
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
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

%patch6 -p0
%patch7 -p0
%patch8 -p0
%patch9 -p0
%patch10 -p0
%patch11 -p0
%patch12 -p0
%patch13 -p0
%patch14 -p0
%patch15 -p0
%patch16 -p0

%build
perl -pi -e 's/^sinclude/dnl sinclude/' configure.in
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

#%%pre
#if [ "$1" = "1" ] ; then
#	if [ ! -n "`getgid jabber`" ]; then
#		/usr/sbin/groupadd -f -g 74 jabber
#	fi
#	if [ ! -n "`id -u jabber 2>/dev/null`" ]; then
#		/usr/sbin/useradd -g jabber -d /var/lib/jabber -u 74 -s /bin/false jabber 2>/dev/null
#	fi
#fi

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
%doc AUTHORS ChangeLog NEWS PROTOCOL README TODO
%doc tools/{migrate.pl,db-setup.mysql,db-setup.pgsql,pipe-auth.pl}
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

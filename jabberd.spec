Summary:	Jabber/XMPP server
Name:		jabberd
Version:	2.0
Release:	0.b1.1
License:	GPL
Group:		Applications/Communications
Source0:	http://www.jabberstudio.org/files/jabberd2/%{name}-%{version}b1.tar.gz
# Source0-md5:	845d023346743b997201873d938fb8f7
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-perlscript.patch
Patch1:		%{name}-binary_path.patch
Patch2:		%{name}-daemonize.patch
URL:		http://jabberd.jabberstudio.org
BuildRequires:	openssl-devel >= 0.9.6b
BuildRequires:	db-devel >= 4.1.24
BuildRequires:	openldap-devel >= 2.1.0
BuildRequires:	postgresql-devel
BuildRequires:	mysql-devel
BuildRequires:	pam-devel
Conflicts:	jabber
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Modern open source Jabber server, implementing latest XMPP protocol.

%prep
%setup -q -n %{name}-%{version}b1
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--bindir="%{_libdir}/%{name}" \
	--enable-authreg="anon db pipe ldap mysql pam pgsql" \
	--enable-storage="db fs mysql pgsql"

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},/var/lib/%{name}/db,/etc/{sysconfig,rc.d/init.d}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

mv $RPM_BUILD_ROOT%{_libdir}/jabberd/jabberd $RPM_BUILD_ROOT%{_bindir}
rm $RPM_BUILD_ROOT%{_sysconfdir}/jabberd{,/templates}/*.dist

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ "$1" = 1 ] ; then
	if [ ! -n "`getgid jabber`" ]; then
		%{_sbindir}/groupadd -f -g 74 jabber
	fi
	if [ ! -n "`id -u jabber 2>/dev/null`" ]; then
		%{_sbindir}/useradd -g jabber -d /var/lib/jabber -u 74 -s /bin/false jabber 2>/dev/null
	fi
fi

%post
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

%postun
# If package is being erased for the last time.
if [ "$1" = "0" ]; then
	%{_sbindir}/userdel jabber 2> /dev/null
	%{_sbindir}/groupdel jabber 2> /dev/null
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog INSTALL NEWS README TODO tools/db-setup.mysql tools/db-setup.pgsql tools/pipe-auth.pl
%dir %{_sysconfdir}/jabberd
%attr(640,root,jabber) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/jabberd/*.cfg
%attr(640,root,jabber) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/jabberd/*.xml
%dir %{_sysconfdir}/jabberd/templates
%attr(640,root,jabber) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/jabberd/templates/*.xml
%attr(755,root,root) %{_bindir}/*
%dir %{_libdir}/jabberd
%attr(755,root,root) %{_libdir}/%{name}/*
%dir %attr(750,root,jabber) /var/lib/%{name}
%dir %attr(750,root,jabber) /var/lib/%{name}/db
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(640,root,root) %config(noreplace) %verify(not md5 size mtime) /etc/sysconfig/%{name}

%{_mandir}/man*/*

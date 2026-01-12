# TODO:
# - SysV init script (scripts/powerman, needs to be PLDified)
# - register systemd service etc.
#
# Conditional build:
%bcond_without	static_libs	# static library
#
Summary:	PowerMan - centralized power control for clusters
Summary(pl.UTF-8):	PowerMan - scentralizowane zarządzanie zasilaniem dla klastrów
Name:		powerman
Version:	2.4.4
Release:	2
License:	GPL v2+
Group:		Applications/System
#Source0Download: https://github.com/chaos/powerman/releases
Source0:	https://github.com/chaos/powerman/releases/download/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	2995c10b1588186abc7bd7c6dd24f0f6
Patch0:		lex.patch
Patch1:		time_t.patch
URL:		https://github.com/chaos/powerman
BuildRequires:	bison
BuildRequires:	curl-devel
BuildRequires:	flex
BuildRequires:	genders-devel
BuildRequires:	jansson-devel
BuildRequires:	ncurses-devel
BuildRequires:	net-snmp-devel
BuildRequires:	pkgconfig
Requires:	%{name}-libs = %{version}-%{release}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# Breaks assert() calls
%define		filterout_cpp	-DNDEBUG

%description
PowerMan is a tool for manipulating remote power control (RPC) devices
from a central location. Several RPC varieties are supported natively
by PowerMan and Expect-like configurability simplifies the addition of
new devices.

%description -l pl.UTF-8
PowerMan to narzędzie do operowanie urządzeniami zdalnego sterowania
zasilaniem (RPC - Remote Power Control) ze scentralizowanego miejsca.
Natywnie przez PowerMana obsługiwane jest kilka rodzajów RPC, a
konfiguracja w stylu Expecta upraszcza dodawanie nowych urządzeń.

%package stonith
Summary:	PowerMan plugin for STONITH interface
Summary(pl.UTF-8):	Wtyczka PowerMan do interfejsu STONITH
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}
Requires:	cluster-glue-stonith

%description stonith
PowerMan plugin for STONITH interface.

%description stonith -l pl.UTF-8
Wtyczka PowerMan do interfejsu STONITH.

%package libs
Summary:	Library for applications using PowerMan
Summary(pl.UTF-8):	Biblioteka dla aplikacji wykorzystujących PowerMan
Group:		Libraries

%description libs
Shared library for applications using PowerMan.

%description libs -l pl.UTF-8
Biblioteka współdzielona dla aplikacji wykorzystujących PowerMan.

%package devel
Summary:	Header files for PowerMan library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki PowerMan
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for PowerMan library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki PowerMan.

%package static
Summary:	Static PowerMan library
Summary(pl.UTF-8):	Statyczna biblioteka PowerMan
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static PowerMan library.

%description static -l pl.UTF-8
Statyczna biblioteka PowerMan.

%prep
%setup -q
%patch -P0 -p1
%patch -P1 -p1

%build
%configure \
	--disable-silent-rules \
	%{!?with_static_libs:--disable-static} \
	--with-genders \
	--with-httppower \
	--with-redfishpower \
	--with-snmppower \
	--with-systemdsystemunitdir=%{systemdunitdir}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%{__mv} $RPM_BUILD_ROOT%{_sysconfdir}/powerman/powerman.conf{.example,}

install -d $RPM_BUILD_ROOT%{systemdtmpfilesdir}
cat >$RPM_BUILD_ROOT%{systemdtmpfilesdir}/powerman.conf <<EOF
d /var/run/powerman 0755 root root -
EOF

# obsoleted by pkg-config
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libpowerman.la

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc DISCLAIMER NEWS.md README.md
%attr(755,root,root) %{_bindir}/pm
%attr(755,root,root) %{_bindir}/powerman
%attr(755,root,root) %{_sbindir}/httppower
%attr(755,root,root) %{_sbindir}/plmpower
%attr(755,root,root) %{_sbindir}/powermand
%attr(755,root,root) %{_sbindir}/redfishpower
%attr(755,root,root) %{_sbindir}/snmppower
%dir %{_sysconfdir}/powerman
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/powerman/powerman.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/powerman/*.dev
%{systemdunitdir}/powerman.service
%{systemdtmpfilesdir}/powerman.conf
%dir /var/run/powerman
%{_mandir}/man1/pm.1*
%{_mandir}/man1/powerman.1*
%{_mandir}/man5/powerman.conf.5*
%{_mandir}/man5/powerman.dev.5*
%{_mandir}/man8/httppower.8*
%{_mandir}/man8/plmpower.8*
%{_mandir}/man8/powermand.8*
%{_mandir}/man8/redfishpower.8*

%files stonith
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/stonith/plugins/external/powerman

%files libs
%defattr(644,root,root,755)
%{_libdir}/libpowerman.so.*.*.*
%ghost %{_libdir}/libpowerman.so.0

%files devel
%defattr(644,root,root,755)
%{_libdir}/libpowerman.so
%{_includedir}/libpowerman.h
%{_pkgconfigdir}/libpowerman.pc
%{_mandir}/man3/libpowerman.3*

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libpowerman.a
%endif

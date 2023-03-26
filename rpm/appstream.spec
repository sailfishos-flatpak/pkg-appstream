%global qt_support 1

# Vala/Vapi support ( upstream disabled by default, probably explains why it the build breaks often )
%global vala 1

Summary: Utilities to generate, maintain and access the AppStream database
Name:    appstream
Version: 0.14.6
Release: 1%{?dist}

# lib LGPLv2+, tools GPLv2+
License: GPLv2+ and LGPLv2+
#URL:     http://www.freedesktop.org/wiki/Distributions/AppStream
URL:     https://github.com/ximion/appstream
Source0: %{name}-%{version}.tar.bz2

Patch1: 0001-Remove-docs-and-tests.patch

# needed for cmake auto-provides
BuildRequires: cmake
BuildRequires: meson >= 0.48
BuildRequires: ccache
BuildRequires: gettext
BuildRequires: gperf
#BuildRequires: gtk-doc
BuildRequires: intltool
#BuildRequires: itstool
#BuildRequires: libstemmer-devel
BuildRequires: pkgconfig(cairo)
BuildRequires: pkgconfig(freetype2)
BuildRequires: pkgconfig(fontconfig)
BuildRequires: pkgconfig(gdk-pixbuf-2.0)
BuildRequires: pkgconfig(gio-2.0)
BuildRequires: pkgconfig(gobject-introspection-1.0)
BuildRequires: pkgconfig(libcurl)
BuildRequires: pkgconfig(libsoup-2.4)
BuildRequires: pkgconfig(librsvg-2.0)
BuildRequires: pkgconfig(libsystemd)
BuildRequires: pkgconfig(libxml-2.0)
BuildRequires: pkgconfig(lmdb)
BuildRequires: pkgconfig(packagekit-glib2)
BuildRequires: pkgconfig(pango)
BuildRequires: pkgconfig(protobuf-lite)
%if %{qt_support}
BuildRequires: pkgconfig(Qt5Core)
%endif
#BuildRequires: pkgconfig(xmlb)
BuildRequires: pkgconfig(yaml-0.1)
# lrelease
%if %{qt_support}
BuildRequires: qt5-qttools-linguist
%endif
BuildRequires: sed
BuildRequires: vala
#BuildRequires: xmlto

Requires: appstream-data

%description
AppStream makes it easy to access application information from the
AppStream database over a nice GObject-based interface.

%package devel
Summary:  Development files for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
# -vala subpackage removed in F30
Obsoletes: appstream-vala < 0.12.4-3
Provides: appstream-vala = %{version}-%{release}
%description devel
%{summary}.

%package compose
Summary: Library for generating AppStream data
Requires: %{name}%{?_isa} = %{version}-%{release}
%description compose
%{summary}.

%package compose-devel
Summary:  Development files for %{name}-compose library
Requires: %{name}-compose%{?_isa} = %{version}-%{release}
Requires: %{name}-devel%{?_isa} = %{version}-%{release}
%description compose-devel
%{summary}.

%if %{qt_support}
%package qt
Summary: Qt5 bindings for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
%description qt
%{summary}.

%package qt-devel
Summary:  Development files for %{name}-qt bindings
Requires: %{name}-qt%{?_isa} = %{version}-%{release}
Requires: pkgconfig(Qt5Core)
%description qt-devel
%{summary}.
%endif


%prep
%autosetup -n %{name}-%{version}/upstream -p1


%build
%{meson} \
 -Dcompose=true \
%if %{qt_support}
 -Dqt=true \
%endif
 -Dvapi=%{?vala:true}%{!?vala:false} \
 -Dstemming=false

%{meson_build}


%install
%{meson_install}

mkdir -p %{buildroot}/var/cache/app-info/{icons,gv,xmls}
touch %{buildroot}/var/cache/app-info/cache.watch

%find_lang appstream

# %if "%{?_metainfodir}" != "%{_datadir}/metainfo"
# # move metainfo to right/legacy location
# mkdir -p %{buildroot}%{_kf5_metainfodir}
# mv %{buildroot}%{_datadir}/metainfo/*.xml \
#    %{buildroot}%{_metainfodir}
# %endif


%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%posttrans
%{_bindir}/appstreamcli refresh --force >& /dev/null ||:

%transfiletriggerin -- %{_datadir}/app-info/xmls
%{_bindir}/appstreamcli refresh --force >& /dev/null ||:

%transfiletriggerpostun -- %{_datadir}/app-info/xmls
%{_bindir}/appstreamcli refresh --force >& /dev/null ||:

%files -f appstream.lang
%doc AUTHORS
#license COPYING
%{_bindir}/appstreamcli
#{_mandir}/man1/appstreamcli.1*
%config(noreplace) %{_sysconfdir}/appstream.conf
%dir %{_libdir}/girepository-1.0/
%{_libdir}/girepository-1.0/AppStream-1.0.typelib
%{_libdir}/libappstream.so.*
%{_datadir}/metainfo/org.freedesktop.appstream.cli.*.xml
# put in -devel? -- rex
%{_datadir}/gettext/its/metainfo.*
%ghost /var/cache/app-info/cache.watch
%dir /var/cache/app-info/
%dir /var/cache/app-info/icons/
%dir /var/cache/app-info/gv/
%dir /var/cache/app-info/xmls/

%files devel
%{_includedir}/appstream/
%{_libdir}/libappstream.so
%{_libdir}/pkgconfig/appstream.pc
%dir %{_datadir}/gir-1.0/
%{_datadir}/gir-1.0/AppStream-1.0.gir
%if 0%{?vala}
%dir %{_datadir}/vala
%dir %{_datadir}/vala/vapi
%{_datadir}/vala/vapi/appstream.deps
%{_datadir}/vala/vapi/appstream.vapi
%endif
# Maybe this should be split out? -- ngompa
#{_datadir}/installed-tests/appstream/metainfo-validate.test

%post -p /sbin/ldconfig compose
%postun -p /sbin/ldconfig compose

%files compose
%{_libexecdir}/appstreamcli-compose
#{_mandir}/man1/appstreamcli-compose.1*
%{_libdir}/libappstream-compose.so.0*
%{_libdir}/girepository-1.0/AppStreamCompose-1.0.typelib
%{_datadir}/metainfo/org.freedesktop.appstream.compose.metainfo.xml

%files compose-devel
%{_includedir}/appstream-compose/
%{_libdir}/libappstream-compose.so
%{_libdir}/pkgconfig/appstream-compose.pc
%{_datadir}/gir-1.0/AppStreamCompose-1.0.gir

%if %{qt_support}
%post -p /sbin/ldconfig qt
%postun -p /sbin/ldconfig qt

%files qt
%{_libdir}/libAppStreamQt.so.*

%files qt-devel
%{_includedir}/AppStreamQt/
%{_libdir}/cmake/AppStreamQt/
%{_libdir}/libAppStreamQt.so
%endif


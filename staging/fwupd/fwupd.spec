%global glib2_version 2.45.8
%global libxmlb_version 0.1.3
%global libgusb_version 0.3.5
%global libcurl_version 7.62.0
%global libjcat_version 0.1.0
%global systemd_version 231
%global json_glib_version 1.1.1

# although we ship a few tiny python files these are utilities that 99.99%
# of users do not need -- use this to avoid dragging python onto CoreOS
%global __requires_exclude ^%{python3}$

# PPC64 is too slow to complete the tests under 3 minutes...
%ifnarch ppc64le
%global enable_tests 1
%endif

%global enable_dummy 1

# fwupd.efi is only available on these arches
%ifarch x86_64 aarch64
%global have_uefi 1
%endif

# gpio.h is only available on these arches
%ifarch x86_64 aarch64
%global have_gpio 1
%endif

# flashrom is only available on these arches
%ifarch i686 x86_64 armv7hl aarch64 ppc64le
%global have_flashrom 1
%endif

%ifarch i686 x86_64
%global have_msr 1
%endif

# Until we actually have seen it outside x86
%ifarch i686 x86_64
%global have_thunderbolt 1
%endif

# only available recently
%if 0%{?fedora} >= 30
%global have_modem_manager 1
%endif

Summary:   Firmware update daemon
Name:      fwupd
Version:   1.9.21
Release:   100.ublue
License:   LGPL-2.1-or-later
URL:       https://github.com/fwupd/fwupd
Source0:   https://people.freedesktop.org/~hughsient/releases/%{name}-%{version}.tar.xz

BuildRequires: gettext
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: libxmlb-devel >= %{libxmlb_version}
BuildRequires: libgudev1-devel
BuildRequires: libgusb-devel >= %{libgusb_version}
BuildRequires: libcurl-devel >= %{libcurl_version}
BuildRequires: libjcat-devel >= %{libjcat_version}
BuildRequires: polkit-devel >= 0.103
BuildRequires: protobuf-c-devel
BuildRequires: python3-packaging
BuildRequires: python3-jinja2
BuildRequires: sqlite-devel
BuildRequires: systemd >= %{systemd_version}
BuildRequires: systemd-devel
BuildRequires: libarchive-devel
BuildRequires: libcbor-devel
%if 0%{?rhel} >= 10 || 0%{?fedora} >= 28
BuildRequires: passim-devel
%endif
BuildRequires: gobject-introspection-devel
%ifarch %{valgrind_arches}
BuildRequires: valgrind
BuildRequires: valgrind-devel
%endif
BuildRequires: gi-docgen
BuildRequires: gnutls-devel
BuildRequires: gnutls-utils
BuildRequires: meson
BuildRequires: json-glib-devel >= %{json_glib_version}
BuildRequires: vala
BuildRequires: pkgconfig(bash-completion)
BuildRequires: git-core
%if 0%{?have_flashrom}
BuildRequires: flashrom-devel >= 1.2-2
%endif
BuildRequires: libdrm-devel

%if 0%{?have_modem_manager}
BuildRequires: ModemManager-glib-devel >= 1.10.0
BuildRequires: libqmi-devel >= 1.22.0
BuildRequires: libmbim-devel
%endif

%if 0%{?have_uefi}
BuildRequires: python3 python3-cairo python3-gobject
BuildRequires: pango-devel
BuildRequires: cairo-devel cairo-gobject-devel
BuildRequires: freetype
BuildRequires: fontconfig
BuildRequires: google-noto-sans-cjk-ttc-fonts
BuildRequires: tpm2-tss-devel >= 2.2.3
%endif

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

Requires: glib2%{?_isa} >= %{glib2_version}
Requires: libxmlb%{?_isa} >= %{libxmlb_version}
Requires: libgusb%{?_isa} >= %{libgusb_version}
Requires: shared-mime-info

Obsoletes: dbxtool < 9
Provides: dbxtool

# optional, but a really good idea
Recommends: udisks2
Recommends: bluez
Recommends: jq
%if 0%{?rhel} >= 10 || 0%{?fedora} >= 28
Recommends: passim
%endif

%if 0%{?have_modem_manager}
Recommends: %{name}-plugin-modem-manager
%endif
%if 0%{?have_flashrom}
Recommends: %{name}-plugin-flashrom
%endif
%if 0%{?have_uefi}
Recommends: %{name}-efi
Recommends: %{name}-plugin-uefi-capsule-data
%endif

%description
fwupd is a daemon to allow session software to update device firmware.

%package devel
Summary: Development package for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Obsoletes: libebitdo-devel < 0.7.5-3
Obsoletes: libdfu-devel < 1.0.0

%description devel
Files for development with %{name}.

%package tests
Summary: Data files for installed tests
Requires: %{name}%{?_isa} = %{version}-%{release}

%description tests
Data files for installed tests.

%if 0%{?have_modem_manager}
%package plugin-modem-manager
Summary: fwupd plugin using ModemManger
Requires: %{name}%{?_isa} = %{version}-%{release}

%description plugin-modem-manager
This provides the optional package which is only required on hardware that
might have mobile broadband hardware. It is probably not required on servers.
%endif

%if 0%{?have_flashrom}
%package plugin-flashrom
Summary: fwupd plugin using flashrom
Requires: %{name}%{?_isa} = %{version}-%{release}

%description plugin-flashrom
This provides the optional package which is only required on hardware that
can be flashed using flashrom. It is probably not required on servers.
%endif

%if 0%{?have_uefi}
%package plugin-uefi-capsule-data
Summary: Localized data for the UEFI UX capsule
Requires: %{name}%{?_isa} = %{version}-%{release}

%description plugin-uefi-capsule-data
This provides the pregenerated BMP artwork for the UX capsule, which allows the
"Installing firmware update…" localized text to be shown during a UEFI firmware
update operation. This subpackage is probably not required on embedded hardware
or server machines.
%endif

%prep
%autosetup -p1

%build

%meson \
    -Ddocs=enabled \
%if 0%{?enable_tests}
    -Dtests=true \
%else
    -Dtests=false \
%endif
%if 0%{?have_flashrom}
    -Dplugin_flashrom=enabled \
%else
    -Dplugin_flashrom=disabled \
%endif
%if 0%{?have_msr}
    -Dplugin_msr=enabled \
%else
    -Dplugin_msr=disabled \
%endif
%if 0%{?have_gpio}
    -Dplugin_gpio=enabled \
%else
    -Dplugin_gpio=disabled \
%endif
%if 0%{?have_uefi}
    -Dplugin_uefi_capsule=enabled \
    -Dplugin_uefi_pk=enabled \
    -Dplugin_tpm=enabled \
    -Defi_binary=false \
%else
    -Dplugin_uefi_capsule=disabled \
    -Dplugin_uefi_pk=disabled \
    -Dplugin_tpm=disabled \
%endif
%if 0%{?have_modem_manager}
    -Dplugin_modem_manager=enabled \
%else
    -Dplugin_modem_manager=disabled \
%endif
    -Dman=true \
    -Dsystemd_unit_user="" \
    -Dbluez=enabled \
    -Dplugin_powerd=disabled \
    -Dlaunchd=disabled \
    -Dsupported_build=enabled \
    -Defi_os_dir="fedora"

%meson_build

%if 0%{?enable_tests}
%check
%meson_test
%endif

%install
%meson_install

mkdir -p --mode=0700 $RPM_BUILD_ROOT%{_localstatedir}/lib/fwupd/gnupg

# workaround for https://bugzilla.redhat.com/show_bug.cgi?id=1757948
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/cache/fwupd

%find_lang %{name}

%post
%systemd_post fwupd.service fwupd-refresh.timer

# change vendor-installed remotes to use the default keyring type
for fn in /etc/fwupd/remotes.d/*.conf; do
    if grep -q "Keyring=gpg" "$fn"; then
        sed -i 's/Keyring=gpg/#Keyring=pkcs/g' "$fn";
    fi
done

%preun
%systemd_preun fwupd.service fwupd-refresh.timer

%postun
%systemd_postun_with_restart fwupd.service fwupd-refresh.timer

%triggerun -- fedora-release-common < 39-0.28
# For upgrades from versions before fwupd-refresh.timer was enabled by default
systemctl --no-reload preset fwupd-refresh.timer &>/dev/null || :

%files -f %{name}.lang
%doc README.md
%license COPYING
%config(noreplace)%{_sysconfdir}/fwupd/fwupd.conf
%dir %{_libexecdir}/fwupd
%{_libexecdir}/fwupd/fwupd
%ifarch x86_64
%{_libexecdir}/fwupd/fwupd-detect-cet
%endif
%{_libexecdir}/fwupd/fwupdoffline
%{_bindir}/dbxtool
%{_bindir}/fwupdmgr
%{_bindir}/fwupdtool
%dir %{_sysconfdir}/fwupd
%dir %{_sysconfdir}/fwupd/bios-settings.d
%{_sysconfdir}/fwupd/bios-settings.d/README.md
%dir %{_sysconfdir}/fwupd/remotes.d
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/lvfs.conf
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/lvfs-testing.conf
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/vendor-directory.conf
%config(noreplace)%{_sysconfdir}/pki/fwupd
%{_sysconfdir}/pki/fwupd-metadata
%if 0%{?have_msr}
/usr/lib/modules-load.d/fwupd-msr.conf
%endif
%{_datadir}/dbus-1/system.d/org.freedesktop.fwupd.conf
%{_datadir}/bash-completion/completions/fwupdmgr
%{_datadir}/bash-completion/completions/fwupdtool
%{_datadir}/fish/vendor_completions.d/fwupdmgr.fish
%{_datadir}/fwupd/metainfo/org.freedesktop.fwupd*.metainfo.xml
%{_datadir}/fwupd/remotes.d/vendor/firmware/README.md
%{_datadir}/dbus-1/interfaces/org.freedesktop.fwupd.xml
%{_datadir}/polkit-1/actions/org.freedesktop.fwupd.policy
%{_datadir}/polkit-1/rules.d/org.freedesktop.fwupd.rules
%{_datadir}/dbus-1/system-services/org.freedesktop.fwupd.service
%{_mandir}/man1/fwupdtool.1*
%{_mandir}/man1/dbxtool.*
%{_mandir}/man1/fwupdmgr.1*
%{_mandir}/man5/*
%{_mandir}/man8/*
%{_datadir}/metainfo/org.freedesktop.fwupd.metainfo.xml
%{_datadir}/icons/hicolor/scalable/apps/org.freedesktop.fwupd.svg
%{_datadir}/fwupd/firmware_packager.py
%{_datadir}/fwupd/simple_client.py
%{_datadir}/fwupd/add_capsule_header.py
%{_datadir}/fwupd/install_dell_bios_exe.py
%{_unitdir}/fwupd-offline-update.service
%{_unitdir}/fwupd.service
%{_unitdir}/fwupd-refresh.service
%{_unitdir}/fwupd-refresh.timer
%{_unitdir}/system-update.target.wants/
%dir %{_localstatedir}/lib/fwupd
%dir %{_localstatedir}/cache/fwupd
%dir %{_datadir}/fwupd/quirks.d
%{_datadir}/fwupd/quirks.d/builtin.quirk.gz
%{_datadir}/doc/fwupd/*.html
%if 0%{?have_uefi}
%config(noreplace)%{_sysconfdir}/grub.d/35_fwupd
%endif
%{_libdir}/libfwupd.so.2*
%{_libdir}/girepository-1.0/Fwupd-2.0.typelib
/usr/lib/udev/rules.d/*.rules
/usr/lib/systemd/system-shutdown/fwupd.shutdown
%dir %{_libdir}/fwupd-%{version}
%{_libdir}/fwupd-%{version}/libfwupd*.so
%ghost %{_localstatedir}/lib/fwupd/gnupg

%if 0%{?have_modem_manager}
%files plugin-modem-manager
%{_libdir}/fwupd-%{version}/libfu_plugin_modem_manager.so
%endif
%if 0%{?have_flashrom}
%files plugin-flashrom
%{_libdir}/fwupd-%{version}/libfu_plugin_flashrom.so
%endif
%if 0%{?have_uefi}
%files plugin-uefi-capsule-data
%{_datadir}/fwupd/uefi-capsule-ux.tar.xz
%endif

%files devel
%{_datadir}/gir-1.0/Fwupd-2.0.gir
%{_datadir}/doc/fwupd/libfwupdplugin
%{_datadir}/doc/fwupd/libfwupd
%{_datadir}/doc/libfwupdplugin
%{_datadir}/doc/libfwupd
%{_datadir}/vala/vapi
%{_includedir}/fwupd-1
%{_libdir}/libfwupd*.so
%{_libdir}/pkgconfig/fwupd.pc

%files tests
%if 0%{?enable_tests}
%{_datadir}/fwupd/host-emulate.d/*.json.gz
%dir %{_datadir}/installed-tests/fwupd
%{_datadir}/installed-tests/fwupd/tests/*
%{_datadir}/installed-tests/fwupd/fwupd-tests.xml
%{_datadir}/installed-tests/fwupd/*.test
%{_datadir}/installed-tests/fwupd/*.cab
%{_datadir}/installed-tests/fwupd/fakedevice124.jcat
%{_datadir}/installed-tests/fwupd/fakedevice124.bin
%{_datadir}/installed-tests/fwupd/fakedevice124.metainfo.xml
%{_datadir}/installed-tests/fwupd/*.sh
%{_datadir}/installed-tests/fwupd/*.zip
%if 0%{?have_uefi}
%{_datadir}/installed-tests/fwupd/efi
%endif
%{_datadir}/installed-tests/fwupd/chassis_type
%{_datadir}/installed-tests/fwupd/sys_vendor
# libgusb >= 0.4.5
%if 0%{?fedora} >= 37 || 0%{?rhel} >= 10
%{_datadir}/fwupd/device-tests/*.json
%endif
%{_libexecdir}/installed-tests/fwupd/*
%{_datadir}/fwupd/remotes.d/fwupd-tests.conf
%endif

%changelog
%autochangelog

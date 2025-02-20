Name:           devpod
# renovate: datasource=github-releases depName=loft-sh/devpod
Version:        v0.6.2
Release:        1%{?dist}
Summary:        Codespaces but open-source, client-only and unopinionated.

License:        MPL-2.0
URL:            https://github.com/loft-sh/%{name}
Source0:        %{url}/releases/download/%{version}/DevPod_linux_x86_64.tar.gz
ExclusiveArch:  x86_64

Requires:       libappindicator-gtk3
Requires:       webkit2gtk4.0

%description
Codespaces but open-source, client-only and unopinionated: Works with any IDE and lets you use any cloud, kubernetes or just localhost docker.

%if 0%{?fedora} == 41
    %global _missing_build_ids_terminate_build 0
    %global debug_package %{nil}
%endif

%prep
%autosetup -c

%install
mkdir -p %{buildroot}%{_bindir}/
mkdir -p %{buildroot}%{_datadir}/
rm -rf usr/bin/xdg-open
rm -rf usr/share/glib-2.0
cp -rf usr/bin/* %{buildroot}%{_bindir}/
cp -rf usr/share/* %{buildroot}%{_datadir}/
rm -rf usr

%files
%{_bindir}/devpod-cli
%{_bindir}/DevPod
%{_datadir}/icons/hicolor/256x256@2/apps/DevPod.png
%{_datadir}/icons/hicolor/128x128/apps/DevPod.png
%{_datadir}/icons/hicolor/32x32/apps/DevPod.png
%{_datadir}/applications/DevPod.desktop

%changelog
* Sun Nov 03 2024 - Zeglius <33781398+Zeglius@users.noreply.github.com>
  - Dummy changelog

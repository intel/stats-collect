%bcond_without tests

Name:		stats-collect
Version:	1.0.8
Release:	1%{?dist}
Summary:	Power, Energy, and Performance configuration tool

License:	BSD-3-Clause
Url:		https://github.com/intel/stats-collect
Source0:	%url/archive/v%{version}/%{name}-%{version}.tar.gz

BuildArch:	noarch

BuildRequires:	python3-devel
%if %{with tests}
BuildRequires:	python3-pytest
%endif
Requires:	python3-stats-collect
Requires:	pepc

%description
Pepc stands for "Power, Energy, and Performance Configurator".
This is a command-line tool for configuring various Linux and Hardware 
power management features.

%package -n python3-%{name}
Summary:	Pepc Python libraries
BuildRequires:	python3-pyyaml
BuildRequires:	python3-paramiko
Requires:	stats-collect

%description -n python3-%{name}
Pepc Python libraries

%prep
%autosetup -n %{name}-%{version}

%build
%py3_build

%install
%py3_install
install -pDm644 docs/man1/stats-collect.1 %{buildroot}/%{_mandir}/man1/stats-collect.1

%check
%if %{with tests}
%pytest
%endif

%files
%doc README.md
%license debian/LICENSE.md
%{_bindir}/stats-collect
%{_mandir}/man1/stats-collect.1*

%files -n python3-%{name}
%{python3_sitelib}/statscollectlibs
%{python3_sitelib}/statscollecttools
%{python3_sitelib}/stats-collect-*.egg-info/

# Date format: date "+%a %b %d %Y"
%changelog
* Fri Jun 24 2022 Artem Bityutskiy <artem.bityutskiy@linux.intel.com> - 1.3.9-1
- Add RPM packaging support.

* Tue Jun 21 2022 Ali Erdinc Koroglu <ali.erdinc.koroglu@intel.com> - 1.3.8-1
- Initial package.

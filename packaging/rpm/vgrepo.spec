########################################################################################

Summary:        Utility for managing Vagrant repositories
Name:           vgrepo
Version:        1.2.0
Release:        0%{?dist}
License:        MIT
Group:          Development/Tools
URL:            https://pypi.python.org/pypi/vgrepo

Source0:        https://github.com/gongled/%{name}/archive/v%{version}.tar.gz
Source1:        %{name}.conf

BuildRequires:  python-clint python-devel python-setuptools

Requires:       python-clint python-setuptools python-packaging PyYAML

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch

Provides:       %{name} = %{verion}-%{release}

########################################################################################

%description
Python tool which provides mechanisms to operate Vagrant images from the repositories.

########################################################################################

%prep
%setup -q -n %{name}-%{version}

%clean
rm -rf %{buildroot}

%build
python setup.py build

%install
rm -rf %{buildroot}
python setup.py install --prefix=%{_prefix} --root=%{buildroot}

install -dm 755 %{buildroot}%{_sysconfdir}
install -pm 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}.conf

########################################################################################

%files
%doc LICENSE README.md
%defattr(-,root,root,-)
%{python_sitelib}/*
%attr(0755,root,root) %{_bindir}/%{name}
%attr(0644,root,root) %{_sysconfdir}/%{name}.conf

########################################################################################

%changelog
* Wed May 10 2017 Gleb Goncharov <gongled@gongled.ru> - 1.2.0-0
- Updated to the latest version

* Tue May 09 2017 Gleb Goncharov <gongled@gongled.ru> - 1.1.0-0
- Updated to the latest version

* Mon May 01 2017 Gleb Goncharov <gongled@gongled.ru> - 1.0.1-0
- Initial build


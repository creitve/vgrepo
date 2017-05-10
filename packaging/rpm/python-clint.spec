########################################################################################

%define package_name      clint

########################################################################################

Summary:        Python Command-line Application Tools
Name:           python-clint
Version:        0.5.1
Release:        0%{?dist}
License:        BSD
Group:          Development/Libraries
URL:            https://github.com/kennethreitz/clint

Source:         https://github.com/kennethreitz/%{package_name}/releases/download/v%{version}/%{package_name}-%{version}.tar.gz

BuildRequires:  python-devel python-setuptools

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}

BuildArch:      noarch

Provides:       %{name} = %{verion}-%{release}

########################################################################################

%description
Command-line application tools with a little documentation, CLI colors and indents,
extermely simple and powerful column printer, interator-based progress bar, implicit
argument handling, simple support for UNIX pipes and application directory management.

########################################################################################

%prep
%setup -qn %{package_name}-%{version}

%clean
rm -rf %{buildroot}

%build
python setup.py build

%install
rm -rf %{buildroot}
python setup.py install --prefix=%{_prefix} --root=%{buildroot}

########################################################################################

%files
%defattr(-,root,root,-)
%{python_sitelib}/*

########################################################################################

%changelog
* Wed May 10 2017 Gleb Goncharov <gongled@gongled.ru> - 0.5.1-0
- Initial build


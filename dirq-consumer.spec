%define python_bin /usr/bin/python
%{!?python_sitelib: %define python_sitelib %(%{python_bin} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Summary: Directory Queue consumer
Name: dirq-consumer
Version: 0.1
Release: 1%{?dist}
License: GPL
Group: Development/Libraries
Source: %{name}.tar.gz
Packager: Omar Pera Mira <campbell.sx@gmail.com>
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Buildarch: noarch
BuildRequires: python-devel
BuildRequires: python-setuptools
Requires: python-messaging
Requires: python-dirq

%description
This module provides a class that abstracts the logic to consume messages from a Messaging Queue. It relies on the
messaging.queue module that provides a generic directory-based queue, and the messaging.message for the abstraction of the message.

%prep
%setup -n %{name}

%build
# Remove CFLAGS=... for noarch packages (unneeded)
# CFLAGS="$RPM_OPT_FLAGS" %{python_bin} setup.py build
%{python_bin} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{python_bin} setup.py install --skip-build --root $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc README.rst

%{python_sitelib}/dirqconsumer/
%{python_sitelib}/dirqconsumer*.egg-info/

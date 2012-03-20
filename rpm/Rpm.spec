#BEGIN_dontchangeme
%if %{?pyver:0}%{!?pyver:1}
	%define pyver 2.5
%endif
%global __python /usr/bin/python%{pyver}
%define pyver_no_dot %(echo %pyver | tr -d ".")
%define python_package python%{pyver_no_dot}
%define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")
%define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")

# Turn off the brp-python-bytecompile script, we'll invoke it again later.
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

%if %{?rel:0}%{!?rel:1}
    %define rel 0
%endif

%if %{?time:0}%{!?time:1}
    %define time 0
%endif
#END_dontchangeme

%if %{?ver:0}%{!?ver:1}
    %define ver 1.0
%endif

%define libname treecompare
%define name %{python_package}-%{libname}

Summary: Compare complex trees of objects with useful diff output and fuzzy matching options.
Name: %{name}
Version: %{ver}
Release: %{rel}.%{time}.demonware
License: BSD
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch
Requires: %{python_package}

Source: %{name}-%{version}.tar.gz

%description
A library for comparing trees of various objects in a way that yields useful "paths" to each difference. Simply knowing that two object blobs differ is hardly useful without knowing where exactly the differences are located. For text blobs, text-diff utilities can solve this problem, but they are ill suited for dealing with arbitrary data structures such as dictionaries where key order doesn't matter.

%prep
%setup

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

# Bytecompile with a specific version of Python.
/usr/lib/rpm/brp-python-bytecompile %{__python}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{python_sitelib}/%{libname}-%{version}-py%{pyver}.egg-info
%{python_sitelib}/%{libname}

%changelog
* Tue Mar 20 2011 Ruy Asan <ruy@demonware.net> - 1.demonware
- Initial build.
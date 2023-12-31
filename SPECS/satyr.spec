%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%if 0%{?fedora} || 0%{?rhel} > 7
# Enable python3 build by default
%bcond_without python3
%else
%bcond_with python3
%endif

%if 0%{?rhel} > 7 || 0%{?fedora} > 28
# Disable python2 build by default
%bcond_with python2
%else
%bcond_without python2
%endif

%if 0%{?suse_version}
  %define python2_sitearch %{python_sitearch}
  %define python2_devel python-devel
  %define libdw_devel libdw-devel
  %define libelf_devel libelf-devel
%else
  %define python2_devel python2-devel
  %define libdw_devel elfutils-devel
  %define libelf_devel elfutils-libelf-devel
%endif

Name: satyr
Version: 0.26
Release: 2%{?dist}
Summary: Tools to create anonymous, machine-friendly problem reports
License: GPLv2+
URL: https://github.com/abrt/satyr
Source0: https://github.com/abrt/%{name}/archive/%{version}/%{name}-%{version}.tar.xz
%if %{with python2}
BuildRequires: %{python2_devel}
%endif # with python2
%if %{with python3}
BuildRequires: python3-devel
%endif # with python3
BuildRequires: %{libdw_devel}
BuildRequires: %{libelf_devel}
BuildRequires: binutils-devel
BuildRequires: rpm-devel
BuildRequires: libtool
BuildRequires: doxygen
BuildRequires: pkgconfig
BuildRequires: automake
BuildRequires: gcc-c++
BuildRequires: gdb
%if %{with python2}
BuildRequires: python2-sphinx
%endif # with python2
%if %{with python3}
BuildRequires: python3-sphinx
%endif # with python3

# git is need for '%%autosetup -S git' which automatically applies all the
# patches above. Please, be aware that the patches must be generated
# by 'git format-patch'
BuildRequires: git

Patch0001: 0001-Anonymize-paths-in-frames.patch
Patch0002: 0002-testsuite-Correct-syntax-for-gdb-backtrace-command.patch


%description
Satyr is a library that can be used to create and process microreports.
Microreports consist of structured data suitable to be analyzed in a fully
automated manner, though they do not necessarily contain sufficient information
to fix the underlying problem. The reports are designed not to contain any
potentially sensitive data to eliminate the need for review before submission.
Included is a tool that can create microreports and perform some basic
operations on them.

%package devel
Summary: Development libraries for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
Development libraries and headers for %{name}.

%if %{with python2}
%package -n python2-satyr
%{?python_provide:%python_provide python2-satyr}
# Remove before F30
Provides: %{name}-python = %{version}-%{release}
Provides: %{name}-python%{?_isa} = %{version}-%{release}
Obsoletes: %{name}-python < 0.24
Summary: Python bindings for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}

%description -n python2-satyr
Python bindings for %{name}.
%endif #with python2

%if %{with python3}
%package -n python3-satyr
%{?python_provide:%python_provide python3-satyr}
# Remove before F30
Provides: %{name}-python3 = %{version}-%{release}
Provides: %{name}-python3%{?_isa} = %{version}-%{release}
Obsoletes: %{name}-python3 < 0.24
Summary: Python 3 bindings for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}

%description -n python3-satyr
Python 3 bindings for %{name}.
%endif # if with python3

%prep
# http://www.rpm.org/wiki/PackagerDocs/Autosetup
# Default '__scm_apply_git' is 'git apply && git commit' but this workflow
# doesn't allow us to create a new file within a patch, so we have to use
# 'git am' (see /usr/lib/rpm/macros for more details)
%define __scm_apply_git(qp:m:) %{__git} am
%autosetup -S git

%build
%configure \
%if %{without python2}
        --without-python2 \
%endif # with python2
%if %{without python3}
        --without-python3 \
%endif # with python3
%{?_without_python2} \
        --disable-static \
        --enable-doxygen-docs

make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}

# Remove all libtool archives (*.la) from modules directory.
find %{buildroot} -name "*.la" | xargs rm --

%check
make check|| {
    # find and print the logs of failed test
    # do not cat tests/testsuite.log because it contains a lot of bloat
    find tests/testsuite.dir -name "testsuite.log" -print -exec cat '{}' \;
    exit 1
}

%if 0%{?fedora} > 27
# ldconfig is not needed
%else
%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig
%endif

%files
%doc README NEWS
%license COPYING
%{_bindir}/satyr
%{_mandir}/man1/%{name}.1*
%{_libdir}/lib*.so.*

%files devel
# The complex pattern below (instead of simlpy *) excludes Makefile{.am,.in}:
%doc apidoc/html/*.{html,png,css,js}
%{_includedir}/*
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*

%if %{with python2}
%files -n python2-satyr
%dir %{python2_sitearch}/%{name}
%{python2_sitearch}/%{name}/*
%{_mandir}/man3/satyr-python.3*
%endif # with python2

%if 0%{?with_python3}
%files -n python3-satyr
%dir %{python3_sitearch}/%{name}
%{python3_sitearch}/%{name}/*
%endif

%changelog
* Fri Jun 29 2018 Matej Habrnal <mhabrnal@redhat.com> 0.26-2
- Anonymize paths in frames
- Test fix: correct syntax for gdb backtrace command

* Tue Apr 17 2018 Matej Habrnal <mhabrnal@redhat.com> 0.26-1
- spec: fix Allow python2 to be optional at build time
- Allow python2 to be optional at build time
- normalization: actualize list of functions
- Append Python interpreter as related package
- makefile: create .tar.xz with make release

* Thu Jan 18 2018 Martin Kutlak <mkutlak@redhat.com> 0.25-1
- New upstream version
 - Normalization: actualize list of functions
 - Fix some compilation warnings
 - Allow to build python3 for rhel8
 - Makefile: add make release-* subcommands
 - Elfutils: Add missing stubs from earlier commit

* Wed Nov 1 2017 Julius Milan <jmilan@redhat.com> 0.24-1
- New upstream version
  - Allow to report unpackaged problems
  - apidoc: generate html docs using doxygen
  - Fix parsing of subset of arm kernel oopses

* Mon Mar 13 2017 Matej Habrnal <mhabrnal@redhat.com> 0.23-1
- New upstream version
  - Allow rpm to be optional at build time
  - Do not use deprecated fedorahosted.org

* Thu Dec 1 2016 Jakub Filak <jakub@thefilaks.net> 0.22-1
- New upstream version
  - Added support fof JavaScript (V8) stack traces
  - Most parts of the in-hook core unwinder callable under unprivileged user
  - GDB core unwinder limits number of unwound frames
  - Fixed a pair of compile warnings - Chris Redmon <credmonster@gmail.com>

* Wed May 18 2016 Matej Habrnal <mhabrnal@redhat.com> 0.21-1
- New upstream version
  - Introduce 'serial' field in uReport
  - normalization: actualize list of functions

Name:      icu4
Version:   4.6
Release:   4.lw
Summary:   International Components for Unicode
Group:     Development/Tools
License:   MIT and UCD and Public Domain
URL:       http://www.icu-project.org/
Source:    http://download.icu-project.org/files/icu4c/4.6/icu4c-4_6-src.tgz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: doxygen, autoconf
Requires: lib%{name} = %{version}-%{release}

Patch1: icu.8198.revert.icu5431.patch
Patch2: icu.8320.freeserif.crash.patch

%description
Tools and utilities for developing with icu.

%package -n lib%{name}
Summary: International Components for Unicode - libraries
Group:   System Environment/Libraries

%description -n lib%{name}
The International Components for Unicode (ICU) libraries provide
robust and full-featured Unicode services on a wide variety of
platforms. ICU supports the most current version of the Unicode
standard, and they provide support for supplementary Unicode
characters (needed for GB 18030 repertoire support).
As computing environments become more heterogeneous, software
portability becomes more important. ICU lets you produce the same
results across all the various platforms you support, without
sacrificing performance. It offers great flexibility to extend and
customize the supplied services.

%package  -n lib%{name}-devel
Summary:  Development files for International Components for Unicode
Group:    Development/Libraries
Requires: lib%{name} = %{version}-%{release}
Requires: pkgconfig

%description -n lib%{name}-devel
Includes and definitions for developing with icu.

%package -n lib%{name}-doc
Summary: Documentation for International Components for Unicode
Group:   Documentation

%description -n lib%{name}-doc
%{summary}.

%prep
%setup -q -n icu
%patch1 -p2 -R -b .icu8198.revert.icu5431.patch
%patch2 -p1 -b .icu8320.freeserif.crash.patch

%build
cd source
sed -i '/AC_PREREQ/s/2.67/2.59/' configure.in

sed -i -e '/^ICUDATA_DIR/s/$(ICULIBSUFFIX)/4/' \
	-e '/^ICUPREFIX/s/icu/%{name}/' \
	-e '/^ICUDATA_BASENAME_VERSION/s/$(ICUPREFIX)/icu/' \
	-e '/^ICUDATA_ENTRY_POINT/s/$(ICUPREFIX)/icu/' \
	-e '/^pkgdatadir/s/$(ICULIBSUFFIX)/4/' icudefs.mk.in 

sed -i -e '/^pkgdatadir/s/$(ICULIBSUFFIX)/4/' \
	-e '/^GENCCODE/s/genccode/genccode4/' \
	-e '/^ICUPKG/s/icupkg/icupkg4/' \
	-e '/^GENCMN/s/gencmn/gencmn4/' \
	-e '/^GENRB/s/genrb/genrb4/' \
	-e '/^PKGDATA/s/pkgdata/pkgdata4/' config/Makefile.inc.in

sed -i -e 's/icu-config/icu4-config/g' -e 's/icu4-config-top/icu-config-top/g' \
	-e 's/icu4-config-bottom/icu-config-bottom/g' \
	tools/pkgdata/pkgdata.1.in tools/pkgdata/pkgdata.cpp \
	Makefile.in configure.in config/icu-config.1.in config/icu-config-bottom \
	config/icu-config-top config/Makefile.inc.in config/mh-linux

sed -i 's/@VERSION@/%{version}/g' config/icu-config.1.in

autoconf
CFLAGS='%optflags -fno-strict-aliasing'
CXXFLAGS='%optflags -fno-strict-aliasing'
%configure --with-data-packaging=library --disable-samples \
	--libdir=%{_libdir}/%{name} \
	--includedir=%{_includedir}/%{name} \
	--oldincludedir=%{_includedir}/%{name}

#rhbz#225896
sed -i 's|-nodefaultlibs -nostdlib||' config/mh-linux
#rhbz#681491
sed -i 's|^LIBS =.*|LIBS = -L../lib -licu4uc -lpthread -lm|' i18n/Makefile
sed -i 's|^LIBS =.*|LIBS = -nostdlib -L../lib -licu4uc -licu4i18n -lc|' io/Makefile
sed -i 's|^LIBS =.*|LIBS = -nostdlib -L../lib -licu4uc -lc|' layout/Makefile
sed -i 's|^LIBS =.*|LIBS = -nostdlib -L../lib -licu4uc -licu4le -lc|' layoutex/Makefile
sed -i 's|^LIBS =.*|LIBS = -nostdlib -L../../lib -licu4tu -licu4uc -lc|' tools/ctestfw/Makefile
sed -i 's|^LIBS =.*|LIBS = -nostdlib -L../../lib -licu4i18n -licu4uc -lpthread -lc|' tools/toolutil/Makefile
# There is no source/doc/html/search/ directory
sed -i '/^\s\+\$(INSTALL_DATA) \$(docsrchfiles) \$(DESTDIR)\$(docdir)\/\$(docsubsrchdir)\s*$/d' Makefile

make # %{?_smp_mflags} # -j(X>1) may "break" man pages as of 3.2, b.f.u #2357
make doc

mv config/icu-config.1.in config/icu4-config.1.in
sed -i -e '/^ICUPREFIX/s/="icu"/="%{name}"/' \
	-e '/${prefix}\/include ${ECHO_C}/s/${prefix}\/include/${includedir}/g' config/icu4-config

%install
rm -rf $RPM_BUILD_ROOT source/__docs
make -C source install DESTDIR=$RPM_BUILD_ROOT
make -C source install-doc docdir=__docs
chmod +x $RPM_BUILD_ROOT%{_libdir}/%{name}/*.so.*

## Rename files to use the 4 prefix
for F in $(ls $RPM_BUILD_ROOT%{_bindir}/ | grep -v icu4); do
	mv $RPM_BUILD_ROOT%{_bindir}/${F} $RPM_BUILD_ROOT%{_bindir}/${F}4
done
mv $RPM_BUILD_ROOT%{_bindir}/icuinfo4 $RPM_BUILD_ROOT%{_bindir}/icu4info

for F in $(ls $RPM_BUILD_ROOT%{_sbindir}/); do
	mv $RPM_BUILD_ROOT%{_sbindir}/${F} $RPM_BUILD_ROOT%{_sbindir}/${F}4 
done
mv $RPM_BUILD_ROOT%{_sbindir}/icupkg4 $RPM_BUILD_ROOT%{_sbindir}/icu4pkg

for F in $(ls $RPM_BUILD_ROOT%{_mandir}/man1/ | grep -v icu4); do
	mv $RPM_BUILD_ROOT%{_mandir}/man1/${F} \
		$RPM_BUILD_ROOT%{_mandir}/man1/$(echo ${F} | sed 's/\.1/4.1/g')
done

for F in $(ls $RPM_BUILD_ROOT%{_mandir}/man8/); do
	mv $RPM_BUILD_ROOT%{_mandir}/man8/${F} \
		$RPM_BUILD_ROOT%{_mandir}/man8/$(echo ${F} | sed 's/\.8/4.8/g')
done
mv $RPM_BUILD_ROOT%{_mandir}/man8/icupkg4.8 $RPM_BUILD_ROOT%{_mandir}/man8/icu4pkg.8

mv $RPM_BUILD_ROOT%{_libdir}/%{name}/pkgconfig $RPM_BUILD_ROOT/%{_libdir}/
for F in $(ls $RPM_BUILD_ROOT%{_libdir}/pkgconfig/); do
	sed -i 's/icu-/icu4-/g' $RPM_BUILD_ROOT%{_libdir}/pkgconfig/${F}
	mv $RPM_BUILD_ROOT%{_libdir}/pkgconfig/${F} \
		$RPM_BUILD_ROOT%{_libdir}/pkgconfig/$(echo ${F} | sed 's/icu-/icu4-/g')
done

install -m0644 $RPM_BUILD_DIR/icu/source/config/icu.pc \
	$RPM_BUILD_ROOT%{_libdir}/pkgconfig/%{name}.pc

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d
cat > $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/%{name}-libs.conf <<EOF
%{_libdir}/%{name}/
EOF

%check
make -C source check

%clean
rm -rf $RPM_BUILD_ROOT
rm -rf $RPM_BUILD_DIR/icu

%post -n lib%{name} -p /sbin/ldconfig

%postun -n lib%{name} -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%{_bindir}/derb4
%{_bindir}/genbrk4
%{_bindir}/gencfu4
%{_bindir}/gencnval4
%{_bindir}/genctd4
%{_bindir}/genrb4
%{_bindir}/makeconv4
%{_bindir}/pkgdata4
%{_bindir}/uconv4
%{_sbindir}/*
%{_mandir}/man1/derb4.1*
%{_mandir}/man1/gencnval4.1*
%{_mandir}/man1/genrb4.1*
%{_mandir}/man1/genbrk4.1*
%{_mandir}/man1/genctd4.1*
%{_mandir}/man1/makeconv4.1*
%{_mandir}/man1/pkgdata4.1*
%{_mandir}/man1/uconv4.1*
%{_mandir}/man8/*.8*

%files -n lib%{name}
%defattr(-,root,root,-)
%doc license.html readme.html
%{_sysconfdir}/ld.so.conf.d/%{name}-libs.conf
%{_libdir}/%{name}/*.so.*

%files -n lib%{name}-devel
%defattr(-,root,root,-)
%{_bindir}/icu4-config
%{_bindir}/icu4info
%{_mandir}/man1/icu4-config.1*
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/layout
%{_includedir}/%{name}/unicode
%{_libdir}/%{name}/*.so
%{_libdir}/pkgconfig/*.pc
%{_libdir}/%{name}
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/%{version}
%{_datadir}/%{name}/%{version}/install-sh
%{_datadir}/%{name}/%{version}/mkinstalldirs
%{_datadir}/%{name}/%{version}/config
%doc %{_datadir}/%{name}/%{version}/license.html

%files -n lib%{name}-doc
%defattr(-,root,root,-)
%doc license.html readme.html
%doc source/__docs/icu/html/*

%changelog
* Wed May 15 2014 Claudio Filho <claudio.filho@locaweb.com.br> - 4.6-4
- Rename libicu to libicu4
- Fix all files to work with libicu 3 without conflicts
- Fix icu4-config
- Add /etc/ld.so.conf.d/icu4-libs.conf

* Tue Apr 22 2014 Claudio Filho <claudio.filho@locaweb.com.br> - 4.6-3
- Remove BuildArch.
- Fix configure.in to change AC_PREREQ version from 2.67 to 2.59.
- Rebult for Locaweb.

* Tue Mar 08 2011 Caolán McNamara <caolanm@redhat.com> - 4.6-2
- Resolves: rhbz#681941 don't link unneccessary -lm, etc.

* Mon Mar 07 2011 Caolán McNamara <caolanm@redhat.com> - 4.6-1
- latest version
- upgrade includes a .pc now of its own, drop ours
- drop integrated icu.6995.kannada.patch
- drop integrated icu.7971.buildfix.patch
- drop integrated icu.7972.buildfix.patch
- drop integrated icu.7932.doublecompare.patch
- drop integrated icu.8011.buildfix.patch

* Fri Feb 11 2011 Caolán McNamara <caolanm@redhat.com> - 4.4.2-8
- Resolves: rhbz#674328 yet more ways that freeserif crashes libicu

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.4.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Feb 03 2011 Caolán McNamara <caolanm@redhat.com> - 4.4.2-6
- Resolves: rhbz#674328 more ways that freeserif crashes libicu

* Wed Feb 02 2011 Caolán McNamara <caolanm@redhat.com> - 4.4.2-5
- Resolves: rhbz#674328 freeserif crashes libicu

* Thu Jan 13 2011 Caolán McNamara <caolanm@redhat.com> - 4.4.2-4
- Resolves: rhbz#669237 strip libicudata

* Mon Nov 29 2010 Caolán McNamara <caolanm@redhat.com> - 4.4.2-3
- Resolves: rhbz#657964 icu-config bindir returns sbindir

* Thu Nov 25 2010 Caolán McNamara <caolanm@redhat.com> - 4.4.2-2
- Resolves: rhbz#654200 revert icu#5431

* Mon Oct 04 2010 Caolán McNamara <caolanm@redhat.com> - 4.4.2-1
- latest version

* Wed Sep 29 2010 jkeating - 4.4.1-6
- Rebuilt for gcc bug 634757

* Wed Sep 22 2010 Caolán McNamara <caolanm@redhat.com> - 4.4.1-5
- upstream patches

* Thu Sep 09 2010 Caolán McNamara <caolanm@redhat.com> - 4.4.1-4
- Resolves: rhbz#631403 doxygen no longer generates gifs

* Thu Jul 08 2010 Caolán McNamara <caolanm@redhat.com> - 4.4.1-3
- move licences into libicu, and add them into the -doc subpackage
  as well

* Wed May 26 2010 Caolán McNamara <caolanm@redhat.com> - 4.4.1-2
- Resolves: rhbz#596171 drop icu.icu6284.strictalias.patch and use
  -fno-strict-aliasig as upstream has added a pile more and doesn't look
  interested in proposed patchs

* Thu Apr 29 2010 Caolán McNamara <caolanm@redhat.com> - 4.4.1-1
- latest version
- drop integrated icu.icu7567.libctest.patch

* Fri Apr 02 2010 Caolán McNamara <caolanm@redhat.com> - 4.4-1
- latest version
- drop integrated icu.6969.pkgdata.patch
- drop integrated icu.icu7039.badextract.patch
- drop integrated icu.XXXX.buildfix.patch

* Wed Dec 02 2009 Caolán McNamara <caolanm@redhat.com> - 4.2.1-8
- Resolves: rhbz#543386 update icu-config

* Thu Nov 19 2009 Caolán McNamara <caolanm@redhat.com> - 4.2.1-7
- Fix FTBFS with yet another autoconf version that changes
  behaviour

* Mon Aug 31 2009 Caolán McNamara <caolanm@redhat.com> - 4.2.1-6
- Resolves: rhbz#520468 fix s390x and other secondary archs

* Tue Jul 28 2009 Caolán McNamara <caolanm@redhat.com> - 4.2.1-5
- icu#7039 fix broken use of extract to get tests working

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 22 2009 Caolán McNamara <caolanm@redhat.com> - 4.2.1-3
- make documentation noarch

* Tue Jul 14 2009 Caolán McNamara <caolanm@redhat.com> - 4.2.1-2
- rpmlint warnings

* Fri Jul 03 2009 Caolán McNamara <caolanm@redhat.com> - 4.2.1-1
- 4.2.1 release

* Fri Jun 26 2009 Caolán McNamara <caolanm@redhat.com> - 4.2.0.1-3
- Resolves: rhbz#508288 multilib conflict

* Thu Jun 11 2009 Caolán McNamara <caolanm@redhat.com> - 4.2.0.1-2
- Resolves: rhbz#505252 add icu.6995.kannada.patch

* Mon Jun 08 2009 Caolán McNamara <caolanm@redhat.com> - 4.2.0.1-1
- 4.2.0.1 release

* Sat May 09 2009 Caolán McNamara <caolanm@redhat.com> - 4.2-1
- 4.2 release

* Sun May 03 2009 Caolán McNamara <caolanm@redhat.com> - 4.2-0.1.d03
- 4.2 release candidate
- drop resolved icu.icu6008.arm.padding.patch
- drop resolved icu.icu6439.bare.elif.patch

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Feb 03 2009 Caolán McNamara <caolanm@redhat.com> - 4.0.1-2
- fix bare elif for gcc-4.4

* Fri Jan 16 2009 Caolán McNamara <caolanm@redhat.com> - 4.0.1-1
- 4.0.1 release

* Mon Dec 29 2008 Caolán McNamara <caolanm@redhat.com> - 4.0-6
- Resolves rhbz#225896 clean up low hanging rpmlint warnings

* Tue Dec 16 2008 Caolán McNamara <caolanm@redhat.com> - 4.0-5
- drop integrated icu.icu5557.safety.patch

* Thu Nov 20 2008 Caolán McNamara <caolanm@redhat.com> - 4.0-4
- annoyingly upstream tarball was repacked apparently to remove 
  some unused/cached dirs

* Sat Sep 06 2008 Caolán McNamara <caolanm@redhat.com> - 4.0-3
- Resolves: rhbz#461348 wrong icu-config

* Tue Aug 26 2008 Caolán McNamara <caolanm@redhat.com> - 4.0-2
- Resolves: rhbz#459698 drop Malayalam patches. Note test with Rachana/Meera
  instead of Lohit Malayalam before filing bugs against icu wrt.
  Malayalam rendering

* Sat Jul 05 2008 Caolán McNamara <caolanm@redhat.com> - 4.0-1
- final release

* Mon Jun 30 2008 Caolán McNamara <caolanm@redhat.com> - 4.0-0.3.d03
- 4.0 release candidate

* Wed Jun 04 2008 Caolán McNamara <caolanm@redhat.com> - 4.0-0.2.d02
- drop icu.icu5498.openoffice.org.patch

* Sun May 31 2008 Caolán McNamara <caolanm@redhat.com> - 4.0-0.1.d02
- 4.0 release candidate
- drop integrated icu.regexp.patch

* Mon May 19 2008 Caolán McNamara <caolanm@redhat.com> - 3.8.1-8
- add icu.icu6284.strictalias.patch and build with 
  strict-aliasing

* Tue Mar 18 2008 Caolán McNamara <caolanm@redhat.com> - 3.8.1-7
- Resolves: rhbz#437761 modify to icu.icu6213.worstcase.patch for
  other worst case expansions

* Mon Mar 17 2008 Caolán McNamara <caolanm@redhat.com> - 3.8.1-6
- Resolves: rhbz#437761 add icu.icu6213.bengali.worstcase.patch

* Mon Feb 04 2008 Caolán McNamara <caolanm@redhat.com> - 3.8.1-5
- Resolves: rhbz#431401 split syllables on 1st 0d4d of a 0d4d + 
  (>= 0d15 && <= 0d39) + 0d4d + 0d30 sequence

* Thu Jan 31 2008 Caolán McNamara <caolanm@redhat.com> - 3.8.1-4
- Resolves: rhbz#431029, rhbz#424661 Remove workaround for 0D31 characters

* Fri Jan 25 2008 Caolán McNamara <caolanm@redhat.com> - 3.8.1-3
- CVE-2007-4770 CVE-2007-4771 add icu.regexp.patch
- Resolves: rhbz#423211 fix malalayam stuff in light of syllable
  changes

* Fri Jan 11 2008 Caolán McNamara <caolanm@redhat.com> - 3.8.1-2
- remove icu.icu5365.dependantvowels.patch and cleanup
  icu.icu5506.multiplevowels.patch as they patch and unpatch 
  eachother (thanks George Rhoten for pointing out that madness)

* Fri Jan 11 2008 Caolán McNamara <caolanm@redhat.com> - 3.8.1-1
- latest version
- drop fixed icu.icu6084.zwnj.notdef.patch

* Thu Dec 13 2007 Caolán McNamara <caolanm@redhat.com> - 3.8-6
- Resolves: rhbz#423211 experimental hack for 0d15+0d4d+0d30

* Tue Dec 11 2007 Caolán McNamara <caolanm@redhat.com> - 3.8-5
- Resolves: rhbz#415541 icu.icu6084.zwnj.notdef.patch

* Wed Nov 28 2007 Caolán McNamara <caolanm@redhat.com> - 3.8-4
- Resolves: ooo#83991 Malayalam "Kartika" font fix

* Tue Nov 13 2007 Caolán McNamara <caolanm@redhat.com> - 3.8-3
- add icu.openoffice.org.patch

* Sat Oct 27 2007 Caolán McNamara <caolanm@redhat.com> - 3.8-2
- add icu.icu6008.arm.padding.patch to fix an arm problem

* Tue Oct 02 2007 Caolán McNamara <caolanm@redhat.com> - 3.8-1
- latest version

* Mon Sep 03 2007 Caolán McNamara <caolanm@redhat.com> - 3.8-0.2.d02
- next release candidate

* Wed Aug 29 2007 Caolán McNamara <caolanm@redhat.com> - 3.8-0.2.d01
- rebuild

* Tue Aug 07 2007 Caolán McNamara <caolanm@redhat.com> - 3.8-0.1.d01
- 3.8 release candidate
- drop integrated icu.icu5433.oriya.patch
- drop integrated icu.icu5488.assamese.patch
- drop integrated icu.icu5500.devicetablecrash.patch
- drop integrated icu.icu5501.sinhala.biggerexpand.patch
- drop integrated icu.icu5594.gujarati.patch
- drop integrated icu.icu5465.telegu.patch

* Wed Jun 13 2007 Caolán McNamara <caolanm@redhat.com> - 3.6-20
- Resolves: rhbz#243984 change the icu group as it is libicu 
  which is "System Environment/Libraries" not icu

* Mon Apr 30 2007 Caolán McNamara <caolanm@redhat.com> - 3.6-19
- Resolves: rhbz#220867 Malayalam rendering

* Tue Feb 13 2007 Caolán McNamara <caolanm@redhat.com> - 3.6-18
- Resolves: rhbz#228457 icu.icu5594.gujarati.patch

* Mon Feb 09 2007 Caolán McNamara <caolanm@redhat.com> - 3.6-17
- spec cleanups

* Mon Feb 05 2007 Caolán McNamara <caolanm@redhat.com> - 3.6-16
- Resolves: rhbz#226949 layout telegu like pango

* Fri Jan 19 2007 Caolán McNamara <caolanm@redhat.com> - 3.6-15
- Resolves: rhbz#214948 icu.icu5506.multiplevowels.patch

* Thu Jan 09 2007 Caolán McNamara <caolanm@redhat.com> - 3.6-14
- Related: rhbz#216089 add icu.icu5557.safety.patch

* Thu Dec 21 2006 Caolán McNamara <caolanm@redhat.com> - 3.6-13
- Resolves: rhbz#220433 modify icu.icu5431.malayam.patch

* Fri Nov 10 2006 Caolán McNamara <caolanm@redhat.com> - 3.6-12
- Resolves: rhbz#214948 icu.icu5506.multiplevowels.patch

* Wed Nov 08 2006 Caolán McNamara <caolanm@redhat.com> - 3.6-11
- Resolves: rhbz#214555 icu.icu5501.sinhala.biggerexpand.patch

* Wed Nov 08 2006 Caolán McNamara <caolanm@redhat.com> - 3.6-10
- Resolves: rhbz#214555 icu.icu5500.devicetablecrash.patch

* Thu Oct 18 2006 Caolán McNamara <caolanm@redhat.com> - 3.6-9
- Resolves: rhbz#213648 extend prev/next to handle ZWJ

* Tue Oct 18 2006 Caolán McNamara <caolanm@redhat.com> - 3.6-8
- Resolves: rhbz213375 (icu.icu5488.assamese.patch)

* Tue Oct 18 2006 Caolán McNamara <caolanm@redhat.com> - 3.6-7
- Resolves: rhbz#211258 (icu.icu5465.telegu.patch)

* Thu Oct 05 2006 Caolán McNamara <caolanm@redhat.com> - 3.6-6
- rh#209391# add icu.icuXXXX.virama.prevnext.patch

* Mon Oct 02 2006 Caolán McNamara <caolanm@redhat.com> - 3.6-5
- rh#208705# add pkg-config Require for -devel package
- add icu.icu5431.malayam.patch for rh#208551#/rh#209084#
- add icu.icu5433.oriya.patch for rh#208559#/rh#209083#

* Sun Oct 01 2006 Jesse Keating <jkeating@redhat.com> - 3.6-4
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Mon Sep 25 2006 Caolán McNamara <caolanm@redhat.com> - 3.6-3
- rh#206615# render malayam like pango

* Wed Sep 06 2006 Caolán McNamara <caolanm@redhat.com> - 3.6-2
- fix rh#205252#/icu#5365 (gnome#121882#/#icu#4026#) to make icu 
  like pango for multiple dependant vowels

* Mon Sep 03 2006 Caolán McNamara <caolanm@redhat.com> - 3.6-1
- final release

* Mon Aug 14 2006 Caolán McNamara <caolanm@redhat.com> - 3.6-0.1.d02
- bump

* Tue Aug 08 2006 Caolán McNamara <caolanm@redhat.com> - 3.6-0.2.d01
- c++ code not alias correct

* Mon Jul 31 2006 Caolán McNamara <caolanm@redhat.com> - 3.6-0.1.d01
- rh#200728# update to prelease 3.6d01 to pick up on sinhala fixes
- drop integrated rh190879.patch
- drop integrated icu-3.4-sinhala1.patch

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 3.4-10.1.1
- rebuild

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 3.4-10.1
- rebuild

* Sat Jun 10 2006 Caolán McNamara <caolanm@redhat.com> - 3.4-10
- rh#194686# BuildRequires

* Tue May 09 2006 Caolán McNamara <caolanm@redhat.com> - 3.4-9
- rh#190879# backport fix

* Wed May 03 2006 Caolán McNamara <caolanm@redhat.com> - 3.4-8
- add Harshula's icu-3.4-sinhala1.patch for some Sinhala support

* Tue May 02 2006 Caolán McNamara <caolanm@redhat.com> - 3.4-7
- add a pkgconfig.pc, make icu-config use it

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 3.4-6.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 3.4-6.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Tue Jan 03 2006 Caolán McNamara <caolanm@redhat.com> - 3.4-6
- add icu-gcc41.patch

* Tue Oct 11 2005 Caolán McNamara <caolanm@redhat.com> - 3.4-5
- clear execstack requirement for libicudata

* Mon Sep 12 2005 Caolán McNamara <caolanm@redhat.com> - 3.4-4
- import extra icu.spec into fedora core for openoffice.org
- build with gcc 4

* Wed Aug 31 2005 Thorsten Leemhuis <fedora at leemhuis.info> - 3.4-3
- Use dist
- gcc32 does not understand -fstack-protector and 
  --param=ssp-buffer-size=4

* Tue Aug  2 2005 Ville Skyttä <ville.skytta at iki.fi> - 3.4-2
- 3.4.

* Sun Jul 31 2005 Ville Skyttä <ville.skytta at iki.fi> - 3.4-0.2.d02
- 3.4-d02.
- Don't ship static libraries.

* Wed Apr 27 2005 Ville Skyttä <ville.skytta at iki.fi> - 3.2-3
- Apply upstream case mapping mutex lock removal patch.
- Build with gcc 3.2 as a temporary workaround for #152495.

* Fri Apr  7 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 3.2-2
- rebuilt

* Sat Jan  1 2005 Ville Skyttä <ville.skytta at iki.fi> - 3.2-1
- Don't use %%{_smp_mflags} (b.f.u #2357).
- Remove unnecessary Epochs.

* Sat Dec  4 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:3.2-0.fdr.1
- Update to 3.2.

* Sun Jul 18 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:3.0-0.fdr.1
- Update to 3.0, datadirs patch no longer needed.
- Package data in shared libs, drop -locales subpackage.
- Rename -docs subpackage to libicu-doc, and generate graphs with graphviz.

* Sat Dec 13 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.6.1-0.fdr.3
- Partial fix for bad datadirs returned by icu-config (works as long as
  data packaging mode is not "common" or "dll").

* Sun Nov 23 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.6.1-0.fdr.2
- First complete version.

* Sun Sep 28 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.6.1-0.fdr.1
- Update to 2.6.1.

* Wed Aug 27 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.6-0.fdr.1
- First build, based on upstream and SuSE 8.2 packages.

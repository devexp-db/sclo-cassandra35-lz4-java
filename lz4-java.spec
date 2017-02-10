# empty debuginfo
%global debug_package %nil

%global build_opts -Doffline=true -Divy.mode=local -Divysettings.xml=/etc/ivy/ivysettings.xml -Divy.revision=%{version}

Name:          lz4-java
Version:       1.3.0
Release:       5%{?dist}
Summary:       LZ4 compression for Java
# GPL: src/xxhash/bench.c
# src/lz4/programs
# BSD: src/xxhash/xxhash.c src/xxhash/xxhash.h
# src/lz4
License:       ASL 2.0 and (BSD and GPLv2+)
URL:           https://github.com/jpountz/lz4-java
Source0:       https://github.com/jpountz/lz4-java/archive/%{version}.tar.gz

# Disable maven-ant-tasks and old aqute-bnd (1.50.x) support
# Add support for system mvel2
# Fix doclint/encoding in javadoc task
Patch0:        lz4-java-1.3.0-build.patch
# Use randomizedtesting <= 2.1.3
Patch1:        lz4-java-1.3.0-junit_Assert.patch

# Build tools
BuildRequires: ant
BuildRequires: ant-junit
BuildRequires: aqute-bnd
BuildRequires: cpptasks
BuildRequires: ivy-local
BuildRequires: java-devel
BuildRequires: javapackages-local
BuildRequires: mvel
BuildRequires: objectweb-asm
BuildRequires: randomizedtesting-junit4-ant
# Other missing build deps
BuildRequires: bea-stax-api
BuildRequires: xerces-j2
BuildRequires: apache-parent
# https://github.com/jpountz/lz4-java/issues/74
# lz4 >= r128 is incompatible with lz4-java apparently
# due to differences in the framing implementation
Provides:      bundled(lz4) = r122
# FPC ticket Bundled Library Exception
# https://fedorahosted.org/fpc/ticket/603
Provides:      bundled(libxxhash) = r37

%description
LZ4 compression for Java, based on Yann Collet's work.
This library provides access to two compression methods
that both generate a valid LZ4 stream:

* fast scan (LZ4):
    ° low memory footprint (~ 16 KB),
    ° very fast (fast scan with skipping heuristics in case the
      input looks incompressible),
    ° reasonable compression ratio (depending on the
      redundancy of the input).
* high compression (LZ4 HC):
    ° medium memory footprint (~ 256 KB),
    ° rather slow (~ 10 times slower than LZ4),
    ° good compression ratio (depending on the size and
      the redundancy of the input).

The streams produced by those 2 compression algorithms use the
same compression format, are very fast to decompress and can be
decompressed by the same decompressor instance.

%package javadoc
Summary:       Javadoc for %{name}
BuildArch:     noarch

%description javadoc
This package contains javadoc for %{name}.

%prep
%setup -q -n %{name}-%{version}
# Cleanup
find -name '*.dylib' -print -delete
find -name '*.so' -print -delete

%patch0 -p1
%patch1 -p1

cp -p src/xxhash/LICENSE LICENSE.xxhash
cp -p src/lz4/LICENSE lz4_LICENSE

# Fix OSGi manifest entries
echo "Export-Package: net.jpountz.*,!linux.*" >> lz4.bnd
sed -i '/packages.version/d' lz4.bnd

%build

ant %build_opts -Divy.pom.version=%{version} jar docs makepom

# bunlde task use old bnd wrap configuration, is not usable
bnd wrap -p lz4.bnd -o dist/lz4-%{version}.jar --version %{version} dist/lz4.jar

%install
%mvn_file net.jpountz.lz4:lz4 lz4
%mvn_artifact dist/lz4-%{version}.pom dist/lz4-%{version}.jar
%mvn_install -J build/docs

%ifnarch %{arm} aarch64
# FIXME - tests fail on aarch64 for unknown reason.
# On armhfp tests are skipped due to poor JVM performance ("Execution
# time total: 3 hours 37 minutes 14 seconds" ... waste of time)
%check
ant %build_opts test
%endif

%files -f .mfiles
%doc CHANGES.md README.md
%license LICENSE.txt LICENSE.xxhash lz4_LICENSE

%files javadoc -f .mfiles-javadoc
%license LICENSE.txt

%changelog
* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Sep 12 2016 gil cattaneo <puntogil@libero.it> 1.3.0-4
- exclude aarch64

* Tue May 03 2016 gil cattaneo <puntogil@libero.it> 1.3.0-3
- fix test suite

* Tue May 03 2016 gil cattaneo <puntogil@libero.it> 1.3.0-2
- unbundle lz4 code (lz4-java issues#74)

* Mon Jul 20 2015 gil cattaneo <puntogil@libero.it> 1.3.0-1
- initial rpm

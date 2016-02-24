# empty debuginfo
%global debug_package %nil

%global build_opts -Doffline=true -Divy.mode=local -Divysettings.xml=/etc/ivy/ivysettings.xml -Divy.revision=%{version}

Name:          lz4-java
Version:       1.3.0
Release:       1%{?dist}
Summary:       LZ4 compression for Java
# GPL: src/xxhash/bench.c
# BSD: src/xxhash/xxhash.c src/xxhash/xxhash.h
License:       ASL 2.0 and (BSD and GPLv2+)
URL:           https://github.com/jpountz/lz4-java
Source0:       https://github.com/jpountz/lz4-java/archive/%{version}.tar.gz

# Disable maven-ant-tasks and old aqute-bnd (1.50.x) support
# Add support for system mvel2
# Fix doclint/encoding in javadoc task
Patch0:        lz4-java-1.3.0-build.patch
# Add system lz4 support
Patch1:        lz4-java-1.3.0-system-lz4.patch
# Disable some random tests failure
Patch2:        lz4-java-1.3.0-test.patch

# Build tools
BuildRequires: ant
BuildRequires: ant-junit
BuildRequires: aqute-bnd
BuildRequires: cpptasks
BuildRequires: ivy-local
BuildRequires: java-devel
BuildRequires: javapackages-local
BuildRequires: lz4-devel
BuildRequires: mvel
BuildRequires: objectweb-asm
BuildRequires: randomizedtesting-junit4-ant
# Other missing build deps
BuildRequires: bea-stax-api
BuildRequires: xerces-j2
BuildRequires: apache-parent
Requires:      lz4%{?_isa}
# Remove when libxxhash become available
# use https://github.com/Cyan4973/xxHash r37
# FPC ticket Bundled Library Exception
# https://fedorahosted.org/fpc/ticket/603
Provides:      bundled(libxxhash) = 37

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
rm -r src/lz4
%patch2 -p1
sed -i 's|${libdir}|%{_libdir}|' build.xml
# TODO src/xxhash
cp -p src/xxhash/LICENSE LICENSE.xxhash

# Fix OSGi manifest entries
echo "Export-Package: net.jpountz.*,!linux.*" >> lz4.bnd
sed -i '/packages.version/d' lz4.bnd

# Use randomizedtesting <= 2.1.3
rm -r \
 src/test/net/jpountz/lz4/AbstractLZ4Test.java \
 src/test/net/jpountz/lz4/LZ4BlockStreamingTest.java \
 src/test/net/jpountz/lz4/LZ4Test.java \
 src/test/net/jpountz/xxhash/XXHash32Test.java \
 src/test/net/jpountz/xxhash/XXHash64Test.java

%build

ant %build_opts -Divy.pom.version=%{version} jar docs makepom

# bunlde task use old bnd wrap configuration, is not usable
bnd wrap -p lz4.bnd -o dist/lz4-%{version}.jar --version %{version} dist/lz4.jar

%install
%mvn_file net.jpountz.lz4:lz4 lz4
%mvn_artifact dist/lz4-%{version}.pom dist/lz4-%{version}.jar
%mvn_install -J build/docs

%ifnarch %{arm}
# Execution time total: 3 hours 37 minutes 14 seconds ... waste of time
%check
ant %build_opts test
%endif

%files -f .mfiles
%doc CHANGES.md README.md
%license LICENSE.txt LICENSE.xxhash

%files javadoc -f .mfiles-javadoc
%license LICENSE.txt

%changelog
* Mon Jul 20 2015 gil cattaneo <puntogil@libero.it> 1.3.0-1
- initial rpm

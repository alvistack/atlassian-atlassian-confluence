%global debug_package %{nil}

%global __strip /bin/true

%global __brp_mangle_shebangs /bin/true

Name: atlassian-confluence
Epoch: 100
Version: 7.18.3
Release: 1%{?dist}
Summary: Atlassian Confluence
License: Apache-2.0
URL: https://www.atlassian.com/software/confluence
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: chrpath
BuildRequires: fdupes
Requires(pre): shadow-utils
Requires: java

%description
Confluence Server is where you create, organise and discuss work with
your team. Capture the knowledge that's too often lost in email inboxes
and shared network drives in Confluence - where it's easy to find, use,
and update. Give every team, project, or department its own space to
create the things they need, whether it's meeting notes, product
requirements, file lists, or project plans, you can get more done in
Confluence.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%install
install -Dpm755 -d %{buildroot}%{_unitdir}
install -Dpm755 -d %{buildroot}/opt/atlassian/confluence
cp -rfT confluence %{buildroot}/opt/atlassian/confluence
install -Dpm644 -t %{buildroot}%{_unitdir} confluence.service
chmod a+x %{buildroot}/opt/atlassian/confluence/bin/start-confluence.sh
chmod a+x %{buildroot}/opt/atlassian/confluence/bin/stop-confluence.sh
find %{buildroot}/opt/atlassian/confluence -type f -name '*.so' -exec chrpath -d {} \;
find %{buildroot}/opt/atlassian/confluence -type f -name '*.bak' -delete
find %{buildroot}/opt/atlassian/confluence -type f -name '*.orig' -delete
find %{buildroot}/opt/atlassian/confluence -type f -name '*.rej' -delete
fdupes -qnrps %{buildroot}/opt/atlassian/confluence

%check

%pre
set -euxo pipefail

CONFLUENCE_HOME=/var/atlassian/application-data/confluence

if [ ! -d $CONFLUENCE_HOME -a ! -L $CONFLUENCE_HOME ]; then
    mkdir -p $CONFLUENCE_HOME
fi

if ! getent group confluence >/dev/null; then
    groupadd \
        --system \
        confluence
fi

if ! getent passwd confluence >/dev/null; then
    useradd \
        --system \
        --gid confluence \
        --home-dir $CONFLUENCE_HOME \
        --no-create-home \
        --shell /usr/sbin/nologin \
        confluence
fi

chown -Rf confluence:confluence $CONFLUENCE_HOME
chmod 0750 $CONFLUENCE_HOME

%post
set -euxo pipefail

CONFLUENCE_CATALINA=/opt/atlassian/confluence

chown -Rf confluence:confluence $CONFLUENCE_CATALINA
chmod 0700 $CONFLUENCE_CATALINA

%files
%license LICENSE
%dir /opt/atlassian
%{_unitdir}/confluence.service
/opt/atlassian/confluence

%changelog

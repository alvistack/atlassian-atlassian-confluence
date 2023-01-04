# Copyright 2022 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%global debug_package %{nil}

%global __strip /bin/true

%global __brp_mangle_shebangs /bin/true

Name: atlassian-confluence
Epoch: 100
Version: 7.19.3
Release: 1%{?dist}
Summary: Atlassian Confluence
License: Apache-2.0
URL: https://www.atlassian.com/software/confluence
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: -post-build-checks
Requires(pre): chrpath
Requires(pre): fdupes
Requires(pre): patch
Requires(pre): shadow-utils
Requires(pre): wget

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
install -Dpm644 -t %{buildroot}%{_unitdir} confluence.service
install -Dpm644 -t %{buildroot}/opt/atlassian/confluence atlassian-confluence.patch

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

CONFLUENCE_DOWNLOAD_URL=http://product-downloads.atlassian.com/software/confluence/downloads/atlassian-confluence-7.19.3.tar.gz
CONFLUENCE_DOWNLOAD_DEST=/tmp/atlassian-confluence-7.19.3.tar.gz
CONFLUENCE_DOWNLOAD_CHECKSUM=ece84ca043548090f9a0a5b898ed18ecbd086107c1c7083ef8a63484ab4f0d07

CONFLUENCE_CATALINA=/opt/atlassian/confluence

wget -c $CONFLUENCE_DOWNLOAD_URL -O $CONFLUENCE_DOWNLOAD_DEST
echo -n "$CONFLUENCE_DOWNLOAD_CHECKSUM $CONFLUENCE_DOWNLOAD_DEST" | sha256sum -c -

mkdir -p $CONFLUENCE_CATALINA
find $CONFLUENCE_CATALINA -mindepth 1 | grep -v atlassian-confluence.patch | xargs rm -rf || echo $?
tar zxf $CONFLUENCE_DOWNLOAD_DEST -C $CONFLUENCE_CATALINA --strip-components=1

cat $CONFLUENCE_CATALINA/atlassian-confluence.patch | patch -p1
chmod a+x $CONFLUENCE_CATALINA/bin/start-confluence.sh
chmod a+x $CONFLUENCE_CATALINA/bin/stop-confluence.sh
find $CONFLUENCE_CATALINA -type f -name '*.so' -exec chrpath -d {} \;
find $CONFLUENCE_CATALINA -type f -name '*.bak' -delete
find $CONFLUENCE_CATALINA -type f -name '*.orig' -delete
find $CONFLUENCE_CATALINA -type f -name '*.rej' -delete
fdupes -qnrps $CONFLUENCE_CATALINA

chown -Rf confluence:confluence $CONFLUENCE_CATALINA
chmod 0700 $CONFLUENCE_CATALINA

%files
%license LICENSE
%dir /opt/atlassian
%dir /opt/atlassian/confluence
%{_unitdir}/confluence.service
/opt/atlassian/confluence/atlassian-confluence.patch

%changelog

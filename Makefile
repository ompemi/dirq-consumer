SPECFILE = dirq-consumer.spec
FILES = ./*
rpmtopdir := $(shell rpm --eval %_topdir)
rpmbuild  := $(shell [ -x /usr/bin/rpmbuild ] && echo rpmbuild || echo rpm)

PACKAGE = $(shell grep -s '^Name'    $(SPECFILE) | sed -e 's/Name: *//')
VERSION = $(shell grep -s '^Version' $(SPECFILE) | sed -e 's/Version: *//')

DISTTAG ?= $(shell lsb_release -r  | sed -nr 's/^[^[:space:]]+[[:space:]]+([0-9]+)\.([0-9]+)$$/.slc\1/p' )
#DISTTAG = ".el6"

#ifneq ($(DISTTAG), .el6)
#ifneq ($(DISTTAG), .el5)
#$(error Only el6/el5 builds are supported.)
#endif
#endif

all: tar rpm

tar:
				mkdir -p $(rpmtopdir)/{SOURCES,SPECS,BUILD,SRPMS,RPMS}
				rm -rf /tmp/$(PACKAGE)
				mkdir /tmp/$(PACKAGE)
				cp -rv $(FILES) /tmp/$(PACKAGE)/
				pwd ; ls -l
				cd /tmp ; tar --exclude .svn --exclude .git -czf $(PACKAGE).tar.gz $(PACKAGE)
				mv -f /tmp/$(PACKAGE).tar.gz $(rpmtopdir)/SOURCES/
				rm -rf /tmp/$(PACKAGE)
				cp -f $(SPECFILE) $(rpmtopdir)/SPECS/$(SPECFILE)

rpm: tar
				$(rpmbuild) -ba --define "dist $(DISTTAG)" $(rpmtopdir)/SPECS/$(SPECFILE)

srpm: tar
				$(rpmbuild) -bs --define "dist $(DISTTAG)" $(rpmtopdir)/SPECS/$(SPECFILE)

sign:
				@echo 'Signs the rpm given, parameter RPMFILE'
				rpmsign --addsign $(RPMFILE)

clean:
				rm $(PACKAGE).tar.gz


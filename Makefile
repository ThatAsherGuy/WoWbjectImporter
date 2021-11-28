VENDORDIR ?= vendor
all: vendor

# WARNING: You need to have pip-compile-multi and pdistx installed from
# pypi before you can build the vendor directory.
vendor: $(VENDORDIR)/__init__.py

$(VENDORDIR)/__init__.py: requirements.txt
	pdistx vendor -r requirements.txt "$(VENDORDIR)"
	sed -i"" -e "s/DataClassDictMixinPath = 'mashumaro.serializer.base.dict.DataClassDictMixin'/DataClassDictMixinPath = 'WoWbjectImporter.vendor.mashumaro.serializer.base.dict.DataClassDictMixin'/g" "$(VENDORDIR)/mashumaro/meta/helpers.py"

requirements.txt: requirements.in
	pip-compile --quiet requirements.in

.PHONY: vendor-update
vendor-update:
	pip-compile --quiet --upgrade requirements.in

test: vendor
	pytest

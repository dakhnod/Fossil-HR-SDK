identifier := $(shell cat build/app.json | jq -r '.identifier')

source_file := app.js
snapshot_file := build/files/code/${identifier}
tools_dir := $(if $(WATCH_SDK_PATH),$(WATCH_SDK_PATH),../../)
package_file := ${identifier}.wapp
package_path := build/${package_file}
adb_target := 192.168.0.192:5555
export_import_dir := /sdcard/Android/data/nodomain.freeyourgadget.gadgetbridge/files
adb_target_dir := ${export_import_dir}/make/${package_file}

.PHONY: all build compile pack push connect install clean

all: build push install
build: compile pack

compile:
	mkdir -p build/files/code build/files/config
	jerry-snapshot generate -f '' ${source_file} -o ${snapshot_file}

pack:
	python3 ${tools_dir}tools/pack.py -i build/ -o ${package_path}

push:
	@if ! adb push ${package_path} ${adb_target_dir}; then \
		echo "Error: Failed to push files."; \
		echo "Check that your phone is connected via adb, and then that the path of the import export directory under the data management screen in Gadgetbridge, corresponds to the export_import_dir in the makefile."; \
		exit 1; \
	fi

connect:
	adb connect ${adb_target}

install:
	adb shell am broadcast \
	-a "nodomain.freeyourgadget.gadgetbridge.Q_UPLOAD_FILE" \
	--es EXTRA_HANDLE APP_CODE \
	--es EXTRA_PATH "${adb_target_dir}" \
	--ez EXTRA_GENERATE_FILE_HEADER false

clean:
	rm -f build/files/code/*
	rm -f build/*.wapp

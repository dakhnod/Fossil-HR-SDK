identifier := $(shell cat build/app.json | jq -r '.identifier')

source_file = app.js
snapshot_file = build/files/code/${identifier}
tools_dir = ../../WatchSDK/tools/
package_file = ${identifier}.wapp
package_path = build/${package_file}

adb_target = 192.168.0.192:5555
adb_target_dir = /sdcard/${package_file}

.PHONY: compile pack all

all: build push install
build: compile pack

compile:
	jerry-snapshot generate -f '' ${source_file} -o ${snapshot_file}

pack:
	python3 ${tools_dir}pack.py build/ ${package_path}

push:
	adb push ${package_path} ${adb_target_dir}

connect:
	adb connect ${adb_target}

install:
	adb shell am broadcast \
    -a "nodomain.freeyourgadget.gadgetbridge.Q_UPLOAD_FILE" \
    --es EXTRA_HANDLE APP_CODE \
    --es EXTRA_PATH "${adb_target_dir}" \
	--ez EXTRA_GENERATE_FILE_HEADER false

clean:
	rm build/files/code/*

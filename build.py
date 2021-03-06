#!/usr/bin/env python

import os
import sys
import subprocess
import json
import re
import errno
from collections import OrderedDict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEPENDENCY_SCRIPT = os.path.join(BASE_DIR, "ensure_dependencies.py")
ABP_DIR = os.path.join(BASE_DIR, "adblockpluschrome")

def get_metadata_path(base_dir, type):
    return os.path.join(BASE_DIR, "metadata." + type)

def get_dev_env_path(base_dir, type):
    return os.path.join(BASE_DIR, "devenv")

def load_translation(locale):
    filename = os.path.join(BASE_DIR, "_locales", locale, "messages.json")
    try:
        file = open(filename, "rb")
    except IOError as e:
        if e.errno != errno.ENOENT:
            raise
        return {}
    with file:
        return json.load(file, object_pairs_hook=OrderedDict)

def process_file(path, data, params):
    if path == "Info.plist":
        return data.replace("org.adblockplus.", "com.betafish.")

    m = re.search(r"^_locales\/([^/]+)\/messages.json$", path)
    if m:
        data = re.sub(r"Adblock Plus", "AdBlock", data, flags=re.I)

        translation = json.loads(data, object_pairs_hook=OrderedDict)
        translation.update(load_translation("en_US"))
        translation.update(load_translation(m.group(1)))

        data = json.dumps(translation, ensure_ascii=False, indent=2)
        data = data.encode('utf-8')

    return data

try:
  subprocess.check_call([sys.executable, DEPENDENCY_SCRIPT, BASE_DIR])
except subprocess.CalledProcessError as e:
  print >>sys.stderr, e
  print >>sys.stderr, "Failed to ensure dependencies being up-to-date!"

import buildtools.packager
buildtools.packager.getMetadataPath = get_metadata_path
buildtools.packager.getDevEnvPath = get_dev_env_path
import buildtools.packagerChrome
buildtools.packagerChrome.processFile = process_file
import buildtools.packagerSafari
buildtools.packagerSafari.processFile = process_file

import buildtools.build
buildtools.build.processArgs(ABP_DIR, sys.argv)

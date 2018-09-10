#!/usr/bin/env python
import argparse
import os
import sys
import shutil
from OpenSSL.crypto import load_pkcs12, FILETYPE_ASN1, sign
import json
import zipfile
import inspect


class PushPackage(object):

    def __init__(self):
        self.REQUIRED_ICONSET_FILES = ["icon_16x16.png", "icon_16x16@2x.png", "icon_32x32.png", "icon_32x32@2x.png", "icon_128x128.png", "icon_128x128@2x.png"]

    def create(self, workdir = './'):
        # create a temporary dir
        tmpdir_path = os.path.join(workdir, 'tmp')
        os.mkdir(tmpdir_path)

        # copy the website.json
        shutil.copyfile(os.path.join(workdir, 'website.json'), os.path.join(tmpdir_path, 'website.json'))

        # copy the uploaded icons
        iconset_path = os.path.join(tmpdir_path, 'icon.iconset')
        os.mkdir(iconset_path)
        for root, dirs, files in os.walk(os.path.join(workdir, './iconset')):
            for file in files:
                shutil.copy(os.path.join(root, file), os.path.join(iconset_path, file))
        
        # create the manifest
        manifest_keys = [os.path.join('icon.iconset', file) for file in self.REQUIRED_ICONSET_FILES]
        manifest_keys += ['website.json']
        manifest_values = [self.sha1_of_file(os.path.join(tmpdir_path, file)) for file in manifest_keys]
        manifest_dict = dict(zip(manifest_keys, manifest_values))
        manifest_path = os.path.join(tmpdir_path, 'manifest.json')
        with open(manifest_path, 'w') as outfile:
            json.dump(manifest_dict, outfile)

        # create the signature file
        current_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
        os.system(os.path.join(current_path, 'script.rb') + ' --tmpdir ' + tmpdir_path)

        # create the zip
        zipf = zipfile.ZipFile(os.path.join(workdir, 'pushPackage.zip'), 'w', zipfile.ZIP_DEFLATED)
        self.zipdir(os.path.join(workdir, 'tmp/'), zipf)
        zipf.close()

        # remove the tmp dir
        if os.path.exists(tmpdir_path):
            shutil.rmtree(tmpdir_path)

    def zipdir(self, path, zip):
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.find(".png") > 0:
                    zip.write(os.path.join(root, file), os.path.join('icon.iconset', file), zipfile.ZIP_DEFLATED)
                else:
                    zip.write(os.path.join(root, file), file, zipfile.ZIP_DEFLATED)

    def sha1_of_file(self, filepath):
        import hashlib
        with open(filepath, 'rb') as f:
            return hashlib.sha1(f.read()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description = "Helper to create pushPackage.zip")
    parser.add_argument("workdir", help="Source dir of the files used to create the zip")
    arguments = parser.parse_args(sys.argv[1:])

    arguments = vars(arguments)

    push_package = PushPackage()
    push_package.create(**arguments)

if __name__ == "__main__":
    main()

import os
import shutil
import glob

import preprocess
import backend


def main():
    # Copy javascript settings files from frontend and remove unneccessary/uninterpretable code
    copy()
    preprocess.main()

    # Interpret the files using node and write the result to ./interpreted/<mode>.json
    modes = glob.glob('source/modes/*_mode.js')
    call_node(modes)
    
    # Create needed folders
    os.popen('rm -r result || true').read()
    os.popen('mkdir result').read()
    os.popen('mkdir result/modes').read()
    os.popen('mkdir result/corpora').read()
    os.popen('mkdir result/attributes').read()
    # Create backend files
    backend.main()


def copy():
    if os.path.exists('source'):
        shutil.rmtree('source')
    os.makedirs('source')
    os.popen('cp -r ../korp-frontend-sb/app/* source/').read()


def call_node(modes):
    os.popen('mkdir node-eval/result || true').read()

    # Run node once per modes-files
    for mode in modes:
        os.popen('cd node-eval; node index.js %s' % mode).read()
    
    os.popen('rm -r source/ || true').read()
    os.popen('rm -r interpreted/ || true').read()
    # This folder will be temporarily used by korp-settings-ws to serve unchanged data to frontend
    os.popen('mv node-eval/result interpreted').read()


if __name__ == '__main__':
    main()


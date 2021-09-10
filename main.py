import os
import shutil

import preprocess
import frontend
import backend


def main():
    copy()
    preprocess.main()
    call_node()
    frontend.main()
    backend.main()


def copy():
    if os.path.exists('source'):
        shutil.rmtree('source')
    os.makedirs('source')
    os.popen('cp -r ../korp-frontend-sb/app/* source/').read()


def call_node():
    os.popen('cd node-eval; node index.js').read()
    # get result files


if __name__ == '__main__':
    main()


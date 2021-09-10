import os
import shutil

import preprocess
import frontend
import backend


def main():
    print('Python says:')
    copy()
    preprocess.main()
    print('Javscript says:')
    call_node()
    print('Python says:')
    os.popen('rm -r result || true').read()
    os.popen('mkdir result').read()

    # os.popen('mkdir result/frontend').read()
    # frontend.main()

    os.popen('mkdir result/modes').read()
    os.popen('mkdir result/corpora').read()
    os.popen('mkdir result/attributes').read()
    backend.main()
    os.popen('rm -r source/ || true').read()


def copy():
    if os.path.exists('source'):
        shutil.rmtree('source')
    os.makedirs('source')
    os.popen('cp -r ../korp-frontend-sb/app/* source/').read()


def call_node():
    os.popen('mkdir node-eval/result').read()
    os.popen('cd node-eval; node index.js').read()
    os.popen('rm -r source').read()
    os.popen('mv node-eval/result source').read()


if __name__ == '__main__':
    main()


import os
import shutil


# 1. Copy files to source
def copy():
    if os.path.exists('source'):
        shutil.rmtree('source')
        
    os.makedirs('source')
        
    os.popen('cp -r ../korp-frontend-sb/app/* source/') 

# 2. Replace all code that shouldn't be there
def remove_bad_code():
    # read common.js and remove stuff about
    with open('source/modes/common.js', 'r') as f:
        lines = f.read().splitlines()
        filter(lambda line: not line.includes('catToString'), lines)
        content = '/n'.join(lines)
    with open('source/app/modes/common.js', 'w') as f:
        f.write(content)

# 3. Run the node project to evaluate files

# 4. Go pack to python and post-process, split into modes, corpora, attributes etc.

def main():
    copy()
    remove_bad_code()


if __name__ == '__main__':
    main()


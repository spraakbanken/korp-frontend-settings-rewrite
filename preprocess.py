import os
import glob


def main():
    fix_commonjs()
    fix_modesjs()


def fix_commonjs():
    filepath = os.path.join(os.getcwd(), './source/modes/common.js')
    # read common.js and remove stuff about catToString
    with open(filepath, 'r') as f:
        lines = f.read().splitlines(keepends=True)
        lines = list(filter(lambda line: 'catToString' not in line, lines))
        content = ''.join(lines)
    with open(filepath, 'w') as f:
        f.write(content)


def fix_modesjs():
    filepaths = glob.glob(os.path.join(os.getcwd(), './source/modes/*'))
    for filepath in filepaths:
        with open(filepath, 'r') as f:
            lines = f.read().splitlines(keepends=True)
            if (filepath.split('/')[-1] == 'npegl_mode.js'):
                lastline = -1
                for idx, line in enumerate(lines):
                    if 'CorpusListing' in line:
                        lastline = idx
                        break
                lines = lines[0:lastline]
            else:
                lines = list(filter(lambda line: 'CorpusListing' not in line, lines))
            content = ''.join(lines)
            
        with open(filepath, 'w') as f:
            f.write(content)


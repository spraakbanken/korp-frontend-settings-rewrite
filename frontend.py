import glob
import json
import os

allowedKeys = ["primaryColor", "primaryLight", "structAttributeSelector", "wordAttributeSelector", "reduceWordAttributeSelector", 
               "wordpicture", "newMapEnabled", "corporafolders", "globalFilterCorpora", "preselectedCorpora", "autocomplete",
               "inputCaseInsensitiveDefault", "statisticsCaseInsensitiveDefault", "hitsPerPageDefault", "hitsPerPageValues",
               "startLang", "defaultOverviewContext", "defaultReadingContext", "defaultWithin", "mapCenter"]


def main():
    for mode, settings in read_files():
        if 'corporafolders' in settings and not settings['corporafolders']:
            del settings['corporafolders']
        for key in list(settings.keys()):
            if key not in allowedKeys:
                settings.pop(key)
        write_mode(mode, settings)
    format_files()


def read_files():
    for filepath in glob.glob('./source/*.json'):
        with open(filepath, 'r') as fp:
            yield filepath.split('/')[-1].split('.')[0], json.load(fp)


def write_mode(mode, settings):
    with open(os.path.join(os.getcwd(), 'result/frontend/', mode + '_mode.js'), 'w') as fp:
        settings_json = json.dumps(settings, indent=4, ensure_ascii=False)
        fp.write("/** @format */ \n export default " + settings_json)

def format_files():
    os.popen('./node-eval/node_modules/prettier/bin-prettier.js --config ../korp-frontend/.prettierrc --write result/frontend').read()

if __name__ == '__main__':
    main()
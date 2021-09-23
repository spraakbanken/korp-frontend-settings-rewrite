import yaml
import os
import glob
import json
from collections import defaultdict

modesKeys = ["primaryColor", "primaryLight", "structAttributeSelector", "wordAttributeSelector", "reduceWordAttributeSelector",
             "wordpicture", "newMapEnabled", "corporafolders", "globalFilterCorpora", "preselectedCorpora", "autocomplete",
             "inputCaseInsensitiveDefault", "statisticsCaseInsensitiveDefault", "hitsPerPageDefault", "hitsPerPageValues",
             "startLang", "defaultOverviewContext", "defaultReadingContext", "defaultWithin", "mapCenter", "mapEnabled"]

corporaKeys = ["id", "title", "description", "attributes", "structAttributes", "customAttributes", "limitedAccess", "context",
               "within", "morphology"]

attributeKeys = ["translation", "opts", "label", "order", "pattern", "customType", "dataset", "extendedComponent", "sidebarInfoUrl",
                 "type", "internalSearch", "externalSearch", "stringify", "displayType", "isStructAttr", "hideSidebar",
                 "hideStatistics", "hideCompare", "ranked", "sidebarComponent"]

extendedComponentKeys = ["name", "options"]  # in options, anything is ok, since this will just be sent to the component

attributeWeirdOnes = ["escape", "extendedTemplate"]


def main():

    modes = {}
    corpora = {}
    attributes = {}

    for mode, settings in read_files():
        modes[mode] = {}
        for key in settings.keys():
            if key != 'corpora':
                if key not in modesKeys:
                    print('Weird key found in %s: %s' % (mode, key))
                elif key == 'corporafolders':
                    new_corpora_folders, corpusToFolder = parse_folders(settings["corporafolders"])
                    modes[mode]["corporafolders"] = new_corpora_folders
                else:
                    modes[mode][key] = settings[key]

        for corpus_id, corpusSettings in settings["corpora"].items():

            p_attrs = corpusSettings.pop('attributes')
            s_attrs = corpusSettings.pop('structAttributes')
            c_attrs = corpusSettings.pop('customAttributes') if 'customAttributes' in corpusSettings else {}

            # first we must see if the attributes has been used before
            for attr_type, attrs in [("attributes", p_attrs), ("structAttributes", s_attrs), ("customAttributes", c_attrs)]:
                for attr_key, attr in attrs.items():
                    check_attribute(attributes, mode, attr_type, corpus_id, attr_key, attr)

            corpusSettings["mode"] = {
                "name": mode,
            }
            if corpusToFolder.get(corpus_id):
                corpusSettings["mode"]["folder"] = corpusToFolder[corpus_id]
            corpora[corpus_id] = corpusSettings

    # TODO sorts keys, but can be fixed

    # dump modes
    for modeId, mode in modes.items():
        with open('./result/modes/' + modeId + '.yaml', 'w', encoding="utf-8") as fp:

            yaml.dump(mode, stream=fp, allow_unicode=True)

    # dump attributes
    with open('./result/attributes/all.yaml', 'w', encoding="utf-8") as fp:
        yaml.dump(attributes, stream=fp, allow_unicode=True)

    # dump corpora
    for corpus_id, corpus in corpora.items():
        with open('./result/corpora/' + corpus_id + '.yaml', 'w', encoding="utf-8") as fp:
            yaml.dump(corpus, stream=fp, allow_unicode=True)


def check_attribute(container, mode, attr_type, corpus_id, attr_key, attr):
    source = '#'.join([mode, corpus_id, attr_type])
    if attr_key not in container:
        # first find of this attribute
        container[attr_key] = []

    found = False
    for content in container[attr_key]:
        attr_alt = content['attribute']
        corpora = content['corpora']
        if compare_dictionaries(attr_alt, attr) == '':
            corpora.append(source)
            found = True
            break
    if not found:
        container[attr_key].append({"attribute": attr, "corpora": [source]})


def parse_folders(outer_folders):
    corpusToFolder = {}

    def recurse(folders):
        new_folders = {}
        for folder_name, folder in folders.items():
            title = folder.pop('title')
            description = folder.pop('description', None)
            contents = folder.pop('contents')
            for corpus in contents:
                corpusToFolder[corpus] = folder_name

            sub_folders = recurse(folder)
            new_folder = {
                "title": title,
                "description": description,
            }
            if sub_folders:
                new_folder["subFolders"] = sub_folders
            new_folders[folder_name] = new_folder
        return new_folders

    new_corpora_folders = recurse(outer_folders)

    return new_corpora_folders, corpusToFolder


def read_files():
    for filepath in glob.glob('./source/*.json'):
        with open(filepath, 'r') as fp:
            yield filepath.split('/')[-1].split('.')[0], json.load(fp)


# from https://stackoverflow.com/questions/27265939/comparing-python-dictionaries-and-nested-dictionaries
def compare_dictionaries(dict_1, dict_2, path=""):
    err = ''
    key_err = ''
    value_err = ''
    old_path = path
    for k in dict_1.keys():
        path = old_path + "[%s]" % k
        if k not in dict_2:
            key_err += "keyerr"
        else:
            if isinstance(dict_1[k], dict) and isinstance(dict_2[k], dict):
                err += compare_dictionaries(dict_1[k], dict_2[k], path)
            else:
                if dict_1[k] != dict_2[k]:
                    value_err += "valueerr"

    for k in dict_2.keys():
        path = old_path + "[%s]" % k
        if k not in dict_1:
            key_err += "keyerr"

    return key_err + value_err + err


if __name__ == '__main__':
    main()

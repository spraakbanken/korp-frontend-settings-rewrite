import yaml
import os
import glob
import json
from collections import defaultdict

# move all these into the config backend, to be used in validation
modesKeys = ["primaryColor", "primaryLight", "structAttributeSelector", "wordAttributeSelector", "reduceWordAttributeSelector",
             "wordpicture", "newMapEnabled", "corporafolders", "globalFilterCorpora", "preselectedCorpora", "autocomplete",
             "inputCaseInsensitiveDefault", "statisticsCaseInsensitiveDefault", "hitsPerPageDefault", "hitsPerPageValues",
             "startLang", "defaultOverviewContext", "defaultReadingContext", "defaultWithin", "mapCenter", "mapEnabled",
             "enableBackendKwicDownload", "enableFrontendKwicDownload"]

corporaKeys = ["id", "title", "description", "attributes", "structAttributes", "customAttributes", "limitedAccess", "context",
               "within", "morphology"]

attributeKeys = ["translation", "opts", "label", "order", "pattern", "customType", "dataset", "extendedComponent", "sidebarInfoUrl",
                 "type", "internalSearch", "externalSearch", "stringify", "displayType", "isStructAttr", "hideSidebar",
                 "hideStatistics", "hideCompare", "ranked", "sidebarComponent"]

# in options, anything is ok, since this will just be sent to the component
extendedComponentKeys = ["name", "options"]

# what are these, are they used?
attributeWeirdOnes = ["escape", "extendedTemplate"]

# these should be removed from modes files
global_settings_keys = ["modeConfig", "visibleModes", "wordPictureConf", "wordpictureTagset", "newsDeskUrl", "logger"]

# these are keys that have been added to settings by mistake and should be removed
ignore_keys = [
    "posset",   
    "fsvlemma", 
    "fsvlex",    
    "fsvvariants",    
    "fsvdescription",    
    "commonStructTypes",
    "kubhist2attributes",
    "kubhist2struct_attributes",
    "fsvattributes",
    "sdhkdescription",
    "sdhkstructs",
    "kubhistattributes",
    "kubhiststruct_attributes",
    "aftonbladstruct_attributes",
    "ubkvtattributes",
    "ubkvtstruct_attributes",
    "runebergattributes",
    "runebergstruct_attributes",
    "interfraStructs",
]

# these should be removed (or rather, not saved) from modes files if value is default
defaults = {
    "autocomplete": True,
    "mapEnabled": False,
    "hitsPerPageDefault": 25,
    "hitsPerPageValues": [25,50,75,100,500,1000],
    "languages": ["sv", "en"],
    "defaultLanguage": "sv",
    "enableBackendKwicDownload": False,
    "enableFrontendKwicDownload": True,
    "downloadFormats": ["csv", "tsv", "annot", "ref"],
    "groupStatistics": ["saldo", "prefix", "suffix", "lex", "lemma", "sense", "text_swefn", "text_blingbring"],
    "wordAttributeSelector": "union",
    "structAttributeSelector": "union",
    "reduceWordAttributeSelector": "intersection",
    "reduceStructAttributeSelector": "intersection",
    "filterSelection": "intersection",
    "primaryColor": "rgb(221, 233, 255)",
    "primaryLight": "rgb(242, 247, 255)",
    "defaultOverviewContext": "1 sentence",
    "defaultReadingContext": "1 paragraph",
    "defaultWithin": {
        "sentence": "sentence"
    },
    "cqpPrio": ['deprel', 'pos', 'msd', 'suffix', 'prefix', 'grundform', 'lemgram', 'saldo', 'word'],

    "defaultOptions": {
        "is": "=",
        "is_not": "!=",
        "starts_with": "^=",
        "contains": "_=",
        "ends_with": "&=",
        "matches": "*=",
        "matches_not": "!*=",
    },

    "korpBackendURL": "https://ws.spraakbanken.gu.se/ws/korp/v8",
    "downloadCgiScript": "https://ws.spraakbanken.gu.se/ws/korp/download",

    "mapCenter": {
        "lat": 62.99515845212052,
        "lng": 16.69921875,
        "zoom": 4
    },
    "readingModeField": "sentence_id",
    "wordpicture": True,
}

def main():

    modes = {}
    corpora = {}
    attributes = {
        'attributes': {},
        'structAttributes': {},
        'customAttributes': {},
    }

    for mode, settings in read_files():
        modes[mode] = {}
        for key in settings.keys():
            if key != 'corpora':
                if (key in defaults and settings[key] == defaults[key]) or key in global_settings_keys:
                    pass
                elif key not in modesKeys:
                    if key not in ignore_keys:
                        print('Weird key found in %s: %s' % (mode, key))
                elif key == 'corporafolders':
                    new_corpora_folders, corpus_to_folder = parse_folders(settings["corporafolders"])
                    if new_corpora_folders != {}:
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
                    check_attribute(attributes[attr_type], corpus_id, attr_key, attr)

            modeFolder = {
                "name": mode,
            }
            if corpus_to_folder.get(corpus_id):
                modeFolder["folder"] = corpus_to_folder[corpus_id]
            if corpus_id in corpora:
                corpora[corpus_id]["mode"].append(modeFolder)
            else:
                corpusSettings["mode"] = [modeFolder]
                corpora[corpus_id] = corpusSettings

    # TODO sorts keys, but can be fixed

    # handles attributes unique to a corpus or attributes that can be grouped
    groups = _fix_attributes(corpora, attributes)

    # gives every attribute a unique identifier and adds identifiers to corpora, removes corpora from attributes
    _fix_attributes2(corpora, attributes)

    print("write groups", len(groups.keys()))
    for group_name in groups.keys():
        with open('./result/attributes/groups/%s.yaml' % group_name, 'w', encoding="utf-8") as fp:
            yaml.dump(groups[group_name], stream=fp, allow_unicode=True)

    print('write final modes', len(modes.keys()))
    for mode_id, mode in modes.items():
        with open('./result/modes/' + mode_id + '.yaml', 'w', encoding="utf-8") as fp:
            yaml.dump(mode, stream=fp, allow_unicode=True)

    print('write pos attributes')
    with open('./result/attributes/pos.yaml', 'w', encoding="utf-8") as fp:
        yaml.dump(attributes['attributes'], stream=fp, allow_unicode=True)
    
    print('write struct attributes')
    with open('./result/attributes/struct.yaml', 'w', encoding="utf-8") as fp:
        yaml.dump(attributes['structAttributes'], stream=fp, allow_unicode=True)

    print('write custom attributes')
    with open('./result/attributes/custom.yaml', 'w', encoding="utf-8") as fp:
        yaml.dump(attributes['customAttributes'], stream=fp, allow_unicode=True)

    # dump corpora
    print('write final corpora', len(corpora.keys()))
    for corpus_id, corpus in corpora.items():
        with open('./result/corpora/' + corpus_id + '.yaml', 'w', encoding="utf-8") as fp:
            yaml.dump(corpus, stream=fp, allow_unicode=True)


def check_attribute(container, corpus_id, attr_key, attr):
    attr['id'] = attr_key
    source = corpus_id
    if attr_key not in container:
        # first find of this attribute
        container[attr_key] = []

    found = False
    for content in container[attr_key]:
        attr_alt = content['attribute']
        corpora = content['corpora']
        if attr_alt == attr:
            if source not in corpora:
                # corpus can be in many modes
                corpora.append(source)
            found = True
            break
    if not found:
        container[attr_key].append({"attribute": attr, "corpora": [source]})


def parse_folders(outer_folders):
    corpus_to_folder = {}

    def recurse(folders, path):
        new_folders = {}
        for folder_name, folder in folders.items():
            title = folder.pop('title')
            description = folder.pop('description', None)
            contents = folder.pop('contents')
            for corpus in contents:
                corpus_to_folder[corpus] = '.'.join([*path, folder_name])

            sub_folders = recurse(folder, [*path, folder_name])
            new_folder = {
                "title": title,
                "description": description,
            }
            if sub_folders:
                new_folder["subFolders"] = sub_folders
            new_folders[folder_name] = new_folder
        return new_folders

    new_corpora_folders = recurse(outer_folders, [])

    return new_corpora_folders, corpus_to_folder


def read_files():
    for filepath in glob.glob('./interpreted/*.json'):
        with open(filepath, 'r') as fp:
            yield filepath.split('/')[-1].split('.')[0], json.load(fp)


def _fix_attributes(corpora_settings, attributes_type_settings):
    """
    move all attributes that are only in one corpus into the actual corpus definition
    

    find common sets of settings that can be used in many corpora (modernAttrs, commonStructAttrs)

    attributes_settings has format
    attr_name: [ { attribute: <attribute setting>, corpora: [ "<mode>#<corpus>#<attributes/structAttributes>", ... ]}  ]
    """

    # corpora, sorted and joined with ',' a list of attributes
    corpusset_to_attributes = {}
    for attr_type, attributes_settings in attributes_type_settings.items():
        for attr_key, attribute_settings in attributes_settings.items():
            delete_idx = []
            for idx, attribute_setting in enumerate(attribute_settings):
                corpora = attribute_setting["corpora"]
                attribute = attribute_setting["attribute"]
                
                if len(corpora) == 1:
                    # is unique attribute, just inline in corpus definintion
                    corpus = corpora[0]
                    asdf = corpora_settings[corpus].get(attr_type, {})
                    asdf[attr_key] = attribute
                    corpora_settings[corpus][attr_type] = asdf

                    delete_idx.append(idx)       
                else:
                    # code to help find groups of attributes

                    # cannot find any modernAttrs :( however lots of other nice groups
                    corpora_group = ",".join(sorted(corpora))
                    attributes_for_corpusset = corpusset_to_attributes.get(corpora_group, {'attributes': {}, 'structAttributes': {}, 'customAttributes': {}})
                    attributes_for_corpusset[attr_type][attribute["id"]] = attribute
                    corpusset_to_attributes[corpora_group] = attributes_for_corpusset

            # remove moved attributes after loop
            for idx in reversed(delete_idx):
                del attribute_settings[idx]
    
    for attr_key in list(attributes_settings.keys()):
        if len(attributes_settings[attr_key]) == 0:
            del attributes_settings[attr_key]
    
    return _create_groups(corpora_settings, corpusset_to_attributes, attributes_type_settings)


def _fix_attributes2(corpora_settings, attributes_type_settings):
    """
    for each attribute in attribute_type_settings, if there are more than one attribute, generate a new name
    then add all attributes to the referecing corpora
    then remove information about corpora from attributes_type_settings
    """
    for attr_type in attributes_type_settings.keys():
        for attr_key in list(attributes_type_settings[attr_type].keys()):
            attributes = attributes_type_settings[attr_type][attr_key]
            # name -> annotation in backend corpora
            # id -> only used to separate attributes in frontend config
            if len(attributes) > 1:
                # must find new ID
                tmp = sorted([(len(thing['attribute'].keys()), thing) for thing in attributes], key=lambda thingWithSize: thingWithSize[0], reverse=True)

                if len(tmp) == 2:
                    biggest_attr = tmp[0][1]
                    smallest_attr = tmp[1][1]
                    biggest_attr['attribute']['id'] = attr_key
                    smallest_attr['attribute']['id'] = attr_key + '_simple'
                    biggest_attr['attribute']['name'] = attr_key
                    smallest_attr['attribute']['name'] = attr_key
                else:
                    for (idx, (_, thing)) in enumerate(tmp):
                        thing['attribute']['id'] = attr_key + ('_' + str(idx) if idx != 0 else '')
                        thing['attribute']['name'] = attr_key
            else:
                # use attr_key as id and name
                attributes[0]['attribute']['id'] = attr_key
                attributes[0]['attribute']['name'] = attr_key

            # remove old object
            del attributes_type_settings[attr_type][attr_key]

            for thing in attributes:
                # add to corpora
                attribute = thing['attribute']
                corpora = thing['corpora']
                for corpus in corpora:
                    refs = corpora_settings[corpus].get(attr_type + 'Ref', [])
                    refs.append(attribute['id'])
                    corpora_settings[corpus][attr_type + 'Ref'] = refs

                # fix data in attribute settings
                attributes_type_settings[attr_type][attribute['id']] = attribute


def _create_groups(corpora_settings, corpusset_to_attributes, attributes_type_settings):
    groups = {}
    for corpora in corpusset_to_attributes.keys():
        attributes_for_corpusset = corpusset_to_attributes[corpora]
        create_group = False
        for attr_type, attr_type_content in attributes_for_corpusset.items():
            if len(attr_type_content.keys()) > 1:
                create_group = True
                break
        if create_group:
            actual_corpora = corpora.split(',')
            # group naming scheme: name of first corpus in group, then number of corpora in group
            # should be improved later, of course
            group_name = actual_corpora[0] + '_' + str(len(actual_corpora))
            while group_name in groups:
                print("group name already used!", group_name)
                group_name = actual_corpora[0] + '_' + actual_corpora[1] + '_' + str(len(actual_corpora))
            for corpus in actual_corpora:
                inherits = corpora_settings[corpus].get("inherits", [])
                inherits.append(group_name)
                corpora_settings[corpus]["inherits"] = inherits
            _remove_groups_from_attributes(actual_corpora, attributes_for_corpusset, attributes_type_settings)
            groups[group_name] = attributes_for_corpusset

    return groups
    

def _remove_groups_from_attributes(corpora, group_attributes, attributes_type_settings):
    """
    removes the attributes that have been moved to groups from the global attributes file    
    """
    for attr_type in group_attributes.keys():
        attr_settings = attributes_type_settings[attr_type]
        for attr_key in group_attributes[attr_type].keys():
            remove_idx = None
            for idx, attr_setting in reversed(list(enumerate(attr_settings[attr_key]))):
                if sorted(attr_setting['corpora']) == sorted(corpora):
                    remove_idx = idx
                    break
            if remove_idx != None:
                del attr_settings[attr_key][remove_idx]
            else:
                raise RuntimeError("Not found", corpora, attr_type, attr_key)
        
        # remove now empty attributes list
        for attr_key in list(attr_settings.keys()):
            if len(attr_settings[attr_key]) == 0:
                del attr_settings[attr_key]


if __name__ == '__main__':
    main()

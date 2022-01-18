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

group_names = {
    "abotidning_180": "saldo",
    "abotidning_184": "prefix-suffix-old",
    "abotidning_266": "date9",
    "abotidning_354": "msd",
    "abotidning_690": "deprel",
    "abotidning_695": "dephead",
    "abotidning_696": "ref",
    "abotidning_699": "pos",
    "abotidning_700": "lemma",
    "abotidning_abounderrattelser2012_699": "lex",
    "abounderrattelser2012_249": "prefix-suffix-removed",

    "abounderrattelser2012_513": "name-tagging",

    "attasidor_27": "sentence-hidden",

    "bellman_354": "dalin",

    "dream-de-open_13": "dream1",
    "dream-en-open_4": "dream2",
    "dream-en-open_5": "dream3",

    "familjeliv-adoption_39": "forum",
}

def main():

    modes = {}
    corpora = {}
    attributes = {
        'attributes': {},
        'structAttributes': {},
        'customAttributes': {},
    }

    # this loop checks default settings values, moves mode and folder info to corpus level and 
    # extracts and removes all attributes from corpus level
    for mode, settings in _read_files():
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
                    _check_attribute(attributes[attr_type], corpus_id, attr_key, attr)

            if mode == 'default' and corpus_id == 'saltnld-sv':
                continue

            modeFolder = {
                "name": mode,
            }
            if corpus_to_folder.get(corpus_id):
                modeFolder["folder"] = corpus_to_folder[corpus_id]
            if corpus_id in ["kubhist2-dalpilen-1910", "kubhist2-kalmar-1910", "kubhist2-dalpilen-1920", "kubhist2-ostgotaposten-1900", "kubhist2-ostgotaposten-1910", "kubhist2-kalmar-1900", "kubhist2-kalmar-kalmarlanstidning-1910", "ogl"]:
                modeFolder["labOnly"] = True

            if corpus_id in corpora:
                corpora[corpus_id]["mode"].append(modeFolder)
            else:
                corpusSettings["mode"] = [modeFolder]
                corpora[corpus_id] = corpusSettings

    # inline label translations
    _inline_label_translations(attributes)

    # first give each attribute a unqiue name
    attributes = _create_unique_names(attributes)

    # inline attributes that are unique to a corpora
    _inline_attributes(corpora, attributes)

    # create groups of attributes that are commonly used together
    groups = _create_groups(corpora, attributes)

    groups = _create_groups_from_groups(corpora, groups)

    print("write groups", len(groups.keys()))
    for group_name in groups.keys():
        with open('./result/attributes/%s.yaml' % group_name, 'w', encoding="utf-8") as fp:
            yaml.dump(groups[group_name], stream=fp, allow_unicode=True)

    print('write final modes', len(modes.keys()))
    for mode_id, mode in modes.items():
        with open('./result/modes/' + mode_id + '.yaml', 'w', encoding="utf-8") as fp:
            yaml.dump(mode, stream=fp, allow_unicode=True)

    # dump corpora
    print('write final corpora', len(corpora.keys()))
    for corpus_id, corpus in corpora.items():
        with open('./result/corpora/' + corpus_id + '.yaml', 'w', encoding="utf-8") as fp:
            yaml.dump(corpus, stream=fp, allow_unicode=True)


def _inline_label_translations(all_attributes):
    en_labels = json.load(open('../korp-frontend-sb/app/translations/corpora-en.json'))
    sv_labels = json.load(open('../korp-frontend-sb/app/translations/corpora-sv.json'))

    remove_sv = set()
    remove_en = set()

    for attr_type, attributes in all_attributes.items():
        for attr_id, attributes2 in attributes.items():
            for attributeasdf in attributes2:
                attribute = attributeasdf['attribute']
                label_id = attribute.get('label', '')

                if label_id != '':
                    # is label is not defined in translation files, use it as is
                    sv_label = sv_labels.get(label_id, label_id)
                    en_label = en_labels.get(label_id, label_id)
                    if sv_label != en_label:
                        label = {
                            'sv': sv_label,
                            'en': en_label
                        }
                    else:
                        label = sv_label
                    attribute['label'] = label

                    if label_id in sv_labels:
                        remove_sv.add(label_id)

                    if label_id in en_labels:
                        remove_en.add(label_id)

    for key in remove_sv:
        del sv_labels[key]
    for key in remove_en:
        del en_labels[key]

    json.dump(en_labels, open('../korp-frontend-sb/app/translations/corpora-en-new.json', 'w'), indent=4, ensure_ascii=False)
    json.dump(sv_labels, open('../korp-frontend-sb/app/translations/corpora-sv-new.json', 'w'), indent=4, ensure_ascii=False)
    

def _check_attribute(attributes, corpus_id, attr_key, attr):
    attr['id'] = attr_key
    source = corpus_id
    if attr_key not in attributes:
        # first find of this attribute
        attributes[attr_key] = []

    found = False
    for content in attributes[attr_key]:
        attr_alt = content['attribute']
        corpora = content['corpora']
        if attr_alt == attr:
            if source not in corpora:
                # corpus can be in many modes
                corpora.append(source)
            found = True
            break
    if not found:
        attributes[attr_key].append({"attribute": attr, "corpora": [source]})


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
            }
            if description:
                new_folder["description"] = description
            if sub_folders:
                new_folder.update(sub_folders)
            new_folders[folder_name] = new_folder
        return new_folders

    new_corpora_folders = recurse(outer_folders, [])

    return new_corpora_folders, corpus_to_folder


def _read_files():
    for filepath in glob.glob('./interpreted/*.json'):
        with open(filepath, 'r') as fp:
            yield filepath.split('/')[-1].split('.')[0], json.load(fp)


def _create_unique_names(global_attributes):
    """
    give each attribute definition a unique name
    """
    new_attributes = {'attributes': {}, 'structAttributes': {}, 'customAttributes': {}}
    for attr_type, attributes_settings in global_attributes.items():
        for attr_key, attribute_settings in attributes_settings.items():
            # name -> annotation in backend corpora
            # id -> only used to separate attributes in frontend config
            if len(attribute_settings) > 1:
                # must find new ID, trying to sort large -> small attributes
                tmp = sorted([(len(thing['attribute'].keys()), thing) for thing in attribute_settings], key=lambda x: x[0], reverse=True)

                # this is a bad attempt to find a good name 
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
                attribute_settings[0]['attribute']['id'] = attr_key
                attribute_settings[0]['attribute']['name'] = attr_key

            for attribute_setting in attribute_settings:
                corpora = attribute_setting["corpora"]
                attribute = attribute_setting["attribute"]

                # save corpora on attribute, to be used later for grouping and also since the 
                # attributes in some way must be added back on corpus configuration
                attribute['corpora'] = corpora
                new_attributes[attr_type][attribute['id']] = attribute

    return new_attributes

def _inline_attributes(corpora_settings, global_attributes):
    """
    move all attributes that are only in one corpus into the actual corpus definition
    """
    for attr_type, attributes in global_attributes.items():
        for attr_key in list(attributes.keys()):
            attribute = attributes[attr_key]
            corpora = attribute["corpora"]

            if len(corpora) == 1:
                # is unique attribute, just inline in corpus definintion
                corpus = corpora[0]
                attrs = corpora_settings[corpus].get(attr_type, {})
                del attribute["corpora"]
                attrs[attr_key] = attribute
                corpora_settings[corpus][attr_type] = attrs
                del attributes[attr_key]


def _create_groups(corpora_settings, global_attributes):

    # corpora, sorted and joined with ',' a list of attributes
    group_to_attributes = {}
    for attr_type, attributes in global_attributes.items():
        for attr_key, attribute in attributes.items():
            corpora = attribute["corpora"]
            # code to help find groups of attributes
            # cannot find any modernAttrs :( however lots of other nice groups
            corpora_group = ",".join(sorted(corpora))
            attributes_for_corpusset = group_to_attributes.get(corpora_group, {'attributes': {}, 'structAttributes': {}, 'customAttributes': {}})
            attributes_for_corpusset[attr_type][attribute["id"]] = attribute
            group_to_attributes[corpora_group] = attributes_for_corpusset

    groups = {}
    for corpora in group_to_attributes.keys():
        group_attributes = group_to_attributes[corpora]

        actual_corpora = corpora.split(',')
        group_name = _get_group_name(actual_corpora, groups)

        for corpus in actual_corpora:
            inherits = corpora_settings[corpus].get("inherits", [])
            inherits.append(group_name)
            corpora_settings[corpus]["inherits"] = inherits
        
        for attr_type, attributes in group_attributes.items():
            for attr_key in attributes.keys():
                del attributes[attr_key]["corpora"]
                del global_attributes[attr_type][attr_key]

        groups[group_name] = group_attributes

    return groups



def _create_groups_from_groups(corpora_settings, groups):
    
    # print(json.dumps(groups, indent=4))
    # import sys
    # sys.exit()
    return groups

    # def loop():

    #     groups_of_groups = {}

    #     for corpus, corpus_settings in list(corpora_settings.items()) + list(groups.items()):
    #         inherits = corpus_settings.get("inherits", [])

    #         for x in range(1, len(inherits)):
    #             group_ids = tuple(inherits[0:x])
    #             if group_ids not in groups_of_groups:
    #                 groups_of_groups[group_ids] = []
    #             groups_of_groups[group_ids].append(corpus)


    #     for group_ids, inheritors in list(groups_of_groups.items()):
    #         if len(inheritors) == 1:
    #             del groups_of_groups[group_ids]        

    #     next = sorted(groups_of_groups.items(), key=lambda item: len(item[0]), reverse=True)[0]

    #     inherits = next[0]
    #     group_name = _get_group_name(next[1], inherits)

    #     for inheritor in next[1]:
    #         if inheritor in corpora_settings:
    #             x = corpora_settings[inheritor]
    #         elif inheritor in groups:
    #             x = groups[inheritor]

    #         # remove the old groups from corpus
    #         x["inherits"] = [group for group in x["inherits"] if group not in inherits]
    #         # and add the new group
    #         x["inherits"].append(group_name)

    #     print("new_group: ", group_name, inherits)
    #     print("used by: ", next[1])

    #     groups[group_name] = {
    #         "inherits": list(inherits)
    #     }

    # while True:
    #     # TODO should crash when group_of_groups becomes empty, but it does not, so there is a bug
    #     loop()

    # return groups


def _get_group_name(corpora, groups):
    # group naming scheme: name of first corpus in group, then number of corpora in group
    # use automatic translation given in group_names
    group_name = corpora[0] + '_' + str(len(corpora))
    while group_name in groups:
        # group name already used!
        group_name = corpora[0] + '_' + corpora[1] + '_' + str(len(corpora))

    # translate the name to a better name
    return group_names.get(group_name, group_name)



if __name__ == '__main__':
    main()

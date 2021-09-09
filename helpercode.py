import json
import glob


def read_modes_files():
    modes = {}
    for mode_filename in glob.glob('resources/source/*'):
        with open(mode_filename) as mode_file:
            # TODO is the character encoding in the response wrong?
            mode_name = mode_filename.split('/')[2].split('.')[0]
            modes[mode_name] = json.load(mode_file)
    return modes


def write_modes_files(modes):
    for mode_name, corpora in modes.items():
        with open('resources/modes/' + mode_name + '.json', 'w') as fp:
            json.dump(list(corpora.keys()), fp)


def extract_information_from_modes(modes):
    corpora = {}
    attributes = {}
    for mode_name, corpora in modes.items():
        for corpora_name, corpora_settings in corpora.items():
            # keep everything as is, except attributes and structAttributes
            attributes = corpora_settings["attributes"]
            struct_attributes = corpora_settings["structAttributes"]
            del corpora_settings["attributes"]
            del corpora_settings["structAttributes"]

            if corpora_name != corpora_settings["id"]:
                print('ERROR corpus key and id should be same? ' + corpora_name + ' ' + corpora_settings["id"])
                exit()

            if corpora.get(corpora_name):
                print("corpus already exists", corpora_name)
            corpora[corpora_name] = corpora_settings
    return corpora, attributes


def write_attributes_to_file(attributes):
    pass


def write_corpora_to_file(modes, attributes):
    pass


def main():
    # reads source files (evaluated from js)
    modes = read_modes_files()
    # creates modes files which only lists the included corpora
    write_modes_files(modes)
    corpora, attributes = extract_information_from_modes(modes)
    write_attributes_to_file(attributes)
    write_corpora_to_file(corpora, attributes)


if __name__ == "__main__":
    main()

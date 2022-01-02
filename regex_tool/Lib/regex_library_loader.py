import json
import os


class regex_lib_processor:

    def __init__(self):
        self.number_format = None
        self.word_format = None
        self.symbol_format = None
        self.text_format = None
        self.name_format = None
        self.library = []

    def get_number_format(self):
        return self.number_format

    # Will need to add a component to load to preexisting json library for all setters
    def set_number_format(self, x):
        if self.number_format:
            self.number_format = x
        else:
            self.number_format

    def get_word_format(self):
        return self.word_format

    def set_word_format(self, x):
        self.word_format = x

    def get_symbol_format(self):
        return self.symbol_format

    def set_symbol_format(self, x):
        self.symbol_format = x

    def get_text_format(self):
        return self.text_format

    def set_text_format(self, x):
        self.text_format = x

    def get_name_format(self):
        return self.name_format

    def set_name_format(self, x):
        self.name_format = x

    def load_regex_lib(self):
        self.library = load_lib()

    def get_library(self):
        if not self.library:
            self.load_regex_lib()
        return self.library


def load_lib(repoDir=None):
    '''
    input a path to the repository/library directory
    :param repoDir:
    :return: json library
    '''
    repo_dir = repoDir
    if repo_dir is not None:
        try:
            repo_file_list = os.listdir(repo_dir)
            if not repo_file_list in [[], [''], '', None]:
                for repo_file in repo_file_list:
                    if repo_file.startswith("regex_library"):
                        with open(os.path.join(repo_dir, repo_file), 'r+') as json_file:
                            return json.load(json_file)
            else:
                # Use default library
                default_path = os.path.join(os.getcwd(),"repo")
                repo_file_list = os.listdir(default_path)
                for repo_file in repo_file_list:
                    if repo_file.startswith("regex_library"):
                        with open(os.path.join(default_path, repo_file), 'r+') as json_file:
                            return json.load(json_file)
        except Exception as e:
            print("%s \nNew Repo folder and/or JSON file will be created!" % e)
            # if not os.path.exists(repo_dir):
            #     os.mkdir(repo_dir)
            return {}
    else:
        return {}

    return {}


def save_lib(repo_lib):
    ROOT = os.getcwd()
    main_dir = os.path.dirname(ROOT)
    repo_file_dir = os.path.join(main_dir, 'repo')
    json_repo_filepath = os.path.join(repo_file_dir, "regex_library.json")
    try:
        json.dump(repo_lib, json_repo_filepath, sort_keys=True, ensure_ascii=False, indent=4)
    except IOError as e:
        print("%s \nNew Repo folder and/or JSON file will be created!" % e)
        if not os.path.exists(repo_file_dir):
            os.mkdir(repo_file_dir)
        json.dump(repo_lib, json_repo_filepath, sort_keys=True, ensure_ascii=False, indent=4)

    return

import os
import shutil
import subprocess
import imp
import inspect
import re

NEW_DIR = './swagger_codegen'
PROJECT_DIR = './swagger_server'
SWAGGER_FILE = './api.yml'

class PrintInColor:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    END = '\033[0m'

    @classmethod
    def error(cls, s, **kwargs):
        print(cls.RED + s + cls.END, **kwargs)

    @classmethod
    def ok(cls, s, **kwargs):
        print(cls.GREEN + s + cls.END, **kwargs)

    @classmethod
    def warning(cls, s, **kwargs):
        print(cls.YELLOW + s + cls.END, **kwargs)

def delete_code_gen_dir():
    """ Delete the codegen directory if exist
    """
    try:
        PrintInColor.ok("DELETING EXISITNG CODEGEN DIRECTORY.")
        shutil.rmtree(NEW_DIR)
    except OSError:
        pass

def codegen():
    """ Run the docker codegen container
    """
    PrintInColor.ok("RUNNING CODEGEN DOCKER CONTAINER.")
    _result = subprocess.check_call(["docker run --rm \
                                    -v ${PWD}:/working swaggerapi/swagger-codegen-cli generate \
                                    -i working/%s \
                                    -l python-flask \
                                    -o /working/swagger_codegen" % SWAGGER_FILE],
                                    shell=True,
                                    stdin=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE)

def delete_and_copy_models():
    """ Delete the project model directory and copy all models
    """
    try:
        PrintInColor.ok("DELETING PROJECT MODEL DIRECTORY.")
        shutil.rmtree("%s/models" % PROJECT_DIR)
    except OSError:
        pass
    PrintInColor.warning("RECREATING PROJECT MODEL DIRECTORY AND COPYING ALL MODELS.")
    shutil.copytree("%s/swagger_server/models" % NEW_DIR, "%s/models" % PROJECT_DIR)

def copy_gend_swagger_file():
    """ Copy the recently gend swagger file
    """
    try:
        os.stat("%s/swagger" % PROJECT_DIR)
    except OSError:
        os.mkdir("%s/swagger" % PROJECT_DIR)
    PrintInColor.warning("COPYING CODEGEN SWAGGER FILE INTO PROJECT.")
    shutil.copy("%s/swagger_server/swagger/swagger.yaml" % NEW_DIR,
                "%s/swagger/swagger.yaml" % PROJECT_DIR)

def copy_base_files():
    """ Copy the base files if non existent
    """
    for src, dst in [("%s/swagger_server/__main__.py" % NEW_DIR, "%s/__main__.py" % PROJECT_DIR),
                     ("%s/swagger_server/encoder.py" % NEW_DIR, "%s/encoder.py" % PROJECT_DIR),
                     ("%s/swagger_server/util.py" % NEW_DIR, "%s/util.py" % PROJECT_DIR),
                     ("%s/requirements.txt" % NEW_DIR, "requirements.txt")]:
        PrintInColor.ok("CHECKING FOR FILE: %s" % dst)
        try:
            os.stat(dst)
            PrintInColor.ok("FILE EXISTS: %s" % dst)
        except OSError:
            PrintInColor.warning("ADDING FILE TO PROJECT: %s" % dst)
            shutil.copy(src, dst)

def make_controller_directory():
    """ Make the project controller directory if it doesn't exist
    """
    try:
        PrintInColor.ok("CHECKING FOR PROJECT CONTROLLER DIRECTORY.")
        os.stat("%s/controllers" % PROJECT_DIR)
        PrintInColor.ok("PROJECT CONTROLLER DIRECTORY FOUND.")
    except OSError:
        PrintInColor.warning("CREATING PROJECT CONTROLLER DIRECTORY.")
        os.mkdir("%s/controllers" % PROJECT_DIR)

def iterate_controllers():
    """ Iterate through the controllers
    """
    for filen in os.listdir("%s/swagger_server/controllers" % NEW_DIR):
        try:
            os.stat("%s/controllers/%s" % (PROJECT_DIR, filen))
            update_controller(filen=filen)
        except OSError:
            PrintInColor.warning("ADDING CONTROLLER TO PROJECT: %s" % filen)
            shutil.copy("%s/swagger_server/controllers/%s" % (NEW_DIR, filen),
                        "%s/controllers/%s" % (PROJECT_DIR, filen))
    for filen in os.listdir("%s/controllers" % (PROJECT_DIR)):
        try:
            os.stat("%s/swagger_server/controllers/%s" % (NEW_DIR, filen))
        except OSError:
            PrintInColor.error("EXTRA CONTROLLER FOUND IN PROJECT: %s" % filen)

def update_controller(filen):
    """ Update a project controller if necessary
    """
    current_fns = find_fns(controller="%s/controllers/%s" % (PROJECT_DIR, filen))
    new_fns = find_fns(controller="%s/swagger_server/controllers/%s" % (NEW_DIR, filen))
    for fn in new_fns:
        existing = [x for x in current_fns if x['details']['name'] == fn['details']['name']]
        if not existing:
            PrintInColor.warning("ADDING FN TO PROJECT CONTROLLER: %s/%s" % (filen, fn['details']['name']))
            with open("%s/controllers/%s" % (PROJECT_DIR, filen), 'a') as fileh:
                fileh.write("\n")
                fileh.write("def %s(%s): %s\n" % (fn['details']['name'], fn['details']['params'], fn['details']['extra']))
                for line in fn['contents']:
                    fileh.write("%s\n" % line)
        if existing:
            if existing[0]['details']['params'] != fn['details']['params']:
                PrintInColor.warning("PARAMS HAVE CHANGED: %s/%s" % (filen, fn['details']['name']))
                print("  CODEGEN: %s" % existing[0]['details']['params'])
                print("  PROJECT: %s" % fn['details']['params'])

def find_fns(controller):
    fn_regex= re.compile(r'''
        ^def\s                                  # start of def
        (?P<name>[a-zA-Z_]+)                    # capture the name of the fn
        \((?P<params>.*)\):                     # (capture the params):
        (?:(?P<extra>.*))                       # any comments etc
        $  ''',                                 # End of line
                             re.VERBOSE)
    with open(controller) as filef:
        controller_contents = filef.read().splitlines()
    fns = []
    fn_contents = []
    details = {}
    capturing = False
    for line in controller_contents:
        if line:
            if line.startswith('def '):
                if capturing:
                    fns.append({"details": details, "contents": fn_contents})
                    fn_contents = []
                result = re.match(fn_regex, line)
                details = result.groupdict()
                capturing = True
            elif capturing:
                fn_contents.append(line)
    if capturing:
        fns.append({"details": details, "contents": fn_contents})
    return sorted(fns, key=lambda k: k['details']['name'])

def main():
    """ Start here
    """
    delete_code_gen_dir()
    codegen()
    delete_and_copy_models()
    copy_gend_swagger_file()
    copy_base_files()
    make_controller_directory()
    iterate_controllers()

if __name__ == '__main__':
    main()

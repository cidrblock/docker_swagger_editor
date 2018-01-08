import os
from modules.codegen_package import CodegenPackage
from modules.project import Project
from modules.dyad import Dyad

PWD = os.path.dirname(os.path.abspath(__file__))
CODEGEN_DIR = "%s/swagger_codegen" % PWD
SWAGGER_FILE = "%s/api.yml" % PWD
PROJECT_DIR = "%s" % PWD


codegen_package = CodegenPackage(directory=CODEGEN_DIR,
                                 swagger_file=SWAGGER_FILE)
codegen_package.generate()

current_project = Project(directory=PROJECT_DIR)
current_project.make_directory(directory='swagger_server', clobber=False)
current_project.remove_trailing_whitespace()

codegen_project = Project(directory=codegen_package.directory)
codegen_project.remove_trailing_whitespace()

dyad = Dyad(src=codegen_project, dst=current_project)
dyad.copy_file(filen='requirements.txt', clobber=False)
dyad.update_directory(directory='swagger_server', clobber=False)
dyad.update_directory(directory='swagger_server/swagger', clobber=True)
dyad.update_directory(directory='swagger_server/models', clobber=True)
dyad.update_directory(directory='swagger_server/controllers', clobber=False)

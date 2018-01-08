""" A codegen object
"""
import shutil
import subprocess
import os
from modules.print_in_color import PrintInColor


class CodegenPackage(object):
    """ A class to hold methods related to codegen
    """
    def __init__(self, directory, swagger_file):
        """ init

        Args:
            directory (string): The directory in which the codegen'd project should be placed

        Returns:
            CodegenPackage: A codegend package

        """
        self.directory = directory
        self.swagger_file = swagger_file

    def generate(self):
        """ Generate a codegen package
        """
        self.delete_codegen_dir()
        self.create_codegen_directory()
        self.codegen()

    def delete_codegen_dir(self):
        """ Delete the codegen directory if exist
        """
        try:
            PrintInColor.message(color='YELLOW', action="deleted", string="EXISITNG CODEGEN DIRECTORY")
            shutil.rmtree(self.directory)
        except OSError:
            pass

    def create_codegen_directory(self):
        """ Create the codegen directory
        """
        PrintInColor.message(color='YELLOW', action="created", string="CODEGEN DIRECTORY")
        os.mkdir(self.directory)

    def codegen(self):
        """ Run the docker codegen container
        """
        PrintInColor.message(color='GREEN', action="running", string="CODEGEN DOCKER CONTAINER")
        try:
            _result = subprocess.check_call(["docker run --rm \
                                             -v %s:/working \
                                             -v %s:/api.yml \
                                             swaggerapi/swagger-codegen-cli generate \
                                             -i /api.yml \
                                             -l python-flask \
                                             -o /working/" % (self.directory,
                                                              self.swagger_file)],
                                            shell=True,
                                            stdin=subprocess.DEVNULL,
                                            stderr=subprocess.DEVNULL,
                                            stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as err:
            PrintInColor.message(color='RED', action="error", string="RUNNING DOCKER")
            print(err)
            raise

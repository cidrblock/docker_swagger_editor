import astor
import ast
import os
import shutil
from modules.print_in_color import PrintInColor

class Dyad(object):
    """ A class to update a dst with a src project
    """

    def __init__(self, src, dst):
        """ init the obj

        Args:
            src (Project): A src project
            dst (Project): A dst project

        """
        self.src = src
        self.dst = dst

    def copy_file(self, filen, clobber=False):
        source = "%s/%s" % (self.src.directory, filen)
        destination = "%s/%s" % (self.dst.directory, filen)
        try:
            os.stat(source)
        except OSError:
            clobber = True
        if clobber:
            shutil.copy(source, destination)
            PrintInColor.message(color='YELLOW', action="created", string=destination)

    def update_directory(self, directory, clobber=False):
        """ update a directory from src to dst

        Args:
            directory (str): The directory to update between the Projects
            clobber (boolean): Nuke the dst before updating

        """
        source = "%s/%s" % (self.src.directory, directory)
        destination = "%s/%s" % (self.dst.directory, directory)
        if clobber:
            try:
                shutil.rmtree(destination)
                PrintInColor.message(color='YELLOW', action="deleted", string=destination)
            except OSError:
                pass
            shutil.copytree(source, destination)
            PrintInColor.message(color='YELLOW', action="updated", string=destination)
        else:
            try:
                os.stat(destination)
            except OSError:
                PrintInColor.message(color='YELLOW', action="created", string=destination)
                os.mkdir(destination)
            for filen in os.listdir(source):
                if os.path.isfile("%s/%s" % (source, filen)):
                    try:
                        os.stat("%s/%s" % (destination, filen))
                        update_file(source=source, destination=destination, filen=filen)
                    except OSError:
                        PrintInColor.message(color='YELLOW', action="created", string="%s/%s" % (destination, filen))
                        shutil.copy("%s/%s" % (source, filen), "%s/%s" % (destination, filen))
            # for filen in os.listdir(destination):
            #     if os.path.isfile("%s/%s" % (destination, filen)):
            #         try:
            #             os.stat("%s/%s" % (source, filen))
            #         except OSError:
            #             PrintInColor.error("EXTRA FILE FOUND: %s/%s" % (destination, filen))

def update_file(source, destination, filen):
    """ update a python file

    Args:
        source (str): The source directory
        destination (str): The destination directory
        filen (str): The name of the file to be updated

    """
    source_tree = astor.code_to_ast.parse_file("%s/%s" % (source, filen))
    destination_tree = astor.code_to_ast.parse_file("%s/%s" % (destination, filen))
    dst_changed = False
    for src_entry in source_tree.body:
        match = False
        for dst_entry in destination_tree.body:
            if astor.dump_tree(src_entry) == astor.dump_tree(dst_entry):
                match = True
                break
        if not match:
            if isinstance(src_entry, ast.Import):
                destination_tree = handle_import(filen, destination_tree, src_entry)
                dst_changed = True
            elif isinstance(src_entry, ast.ImportFrom):
                destination_tree = handle_import_from(filen, destination_tree, src_entry)
                dst_changed = True
            elif isinstance(src_entry, ast.FunctionDef):
                destination_tree, dst_changed = handle_function_def(filen,
                                                                    destination_tree,
                                                                    src_entry)
            else:
                PrintInColor.message(color='RED', action="unhandled", string=filen)
                print("-> %s" % astor.to_source(src_entry))
    if dst_changed:
        destination_tree = sort_defs(destination_tree)
        with open("%s/%s" % (destination, filen), 'w') as fh:
            fh.write(astor.to_source(destination_tree))
    else:
        PrintInColor.message(color='GREEN', action="unmodified", string="%s/%s" % (destination, filen))

def handle_import(filen, destination_tree, src_entry):
    """ Add a missing import statement

    Args:
        filen (str): The nname of the file being modified
        destination_tree (ast): An ast generated from the destination file
        src_entry (ast node): An ast node found missing from the destination_tree

    """
    PrintInColor.message(color='YELLOW', action="updated", string=filen)
    print("SRC-> %s" % astor.to_source(src_entry))
    destination_tree.body.insert(0, src_entry)
    return destination_tree

def handle_import_from(filen, destination_tree, src_entry):
    """ Add or modify a 'from' statement

    Args:
        filen (str): The nname of the file being modified
        destination_tree (ast): An ast generated from the destination file
        src_entry (ast node): An ast node found missing from the destination_tree

    """
    modified_import_from = False
    for i, dst_entry in enumerate(destination_tree.body):
        if isinstance(dst_entry, ast.ImportFrom):
            if dst_entry.module == src_entry.module:
                PrintInColor.message(color='YELLOW', action="updated", string=filen)
                print("SRC-> %s" % astor.to_source(src_entry))
                print("DST-> %s" % astor.to_source(dst_entry))
                destination_tree.body[i] = src_entry
                modified_import_from = True
                dst_changed = True
    if not modified_import_from:
        destination_tree.body.insert(0, src_entry)
        PrintInColor.message(color='YELLOW', action="updated", string=filen)
        print("SRC-> %s" % astor.to_source(src_entry))
        dst_changed = True
    return destination_tree

def handle_function_def(filen, destination_tree, src_entry):
    """ Add or modify a 'def'

    Args:
        filen (str): The nname of the file being modified
        destination_tree (ast): An ast generated from the destination file
        src_entry (ast node): An ast node found missing from the destination_tree

    """
    found_by_name = False
    dst_changed = False
    for i, dst_entry in enumerate(destination_tree.body):
        if isinstance(dst_entry, ast.FunctionDef):
            if dst_entry.name == src_entry.name:
                found_by_name = True
                if astor.to_source(dst_entry.args) != astor.to_source(src_entry.args):
                    PrintInColor.message(color='RED', action="discrepancy", string=filen)
                    print("DEF-> %s" % src_entry.name)
                    print("----SRC----")
                    PrintInColor.code(string=astor.to_source(src_entry.args))
                    print("----DST----")
                    PrintInColor.code(string=astor.to_source(dst_entry.args))
                    dst_changed = False
                elif astor.to_source(dst_entry.body[0]) != astor.to_source(src_entry.body[0]):
                    if isinstance(src_entry.body[0], ast.Expr):
                        if isinstance(dst_entry.body[0], ast.Expr):
                            PrintInColor.message(color='YELLOW', action="updated", string=filen)
                            print("DEF-> %s (docstring updated)" % src_entry.name)
                            print("----SRC----")
                            PrintInColor.code(string=astor.to_source(src_entry.body[0]))
                            print("----DST----")
                            PrintInColor.code(string=astor.to_source(dst_entry.body[0]))
                            destination_tree.body[i].body[0] = src_entry.body[0]
                            dst_changed = True
                        else:
                            PrintInColor.message(color='YELLOW', action="updated", string=filen)
                            print("DEF-> %s (docstring added)" % src_entry.name)
                            print("----SRC----")
                            PrintInColor.code(string=astor.to_source(src_entry.body[0]))
                            destination_tree.body[i].body.insert(0, src_entry.body[0])
                            dst_changed = True
                else:
                    PrintInColor.message(color='YELLOW', action="unmodified", string="(different) %s/%s" % (filen, src_entry.name))

    if not found_by_name:
        destination_tree.body.append(src_entry)
        PrintInColor.message(color='YELLOW', action="updated", string=filen)
        print("----SRC----")
        PrintInColor.code(string=astor.to_source(src_entry))
        dst_changed = True
    return destination_tree, dst_changed

def sort_defs(destination_tree):
    defs = []
    for i in reversed(range(len(destination_tree.body))):
        if isinstance(destination_tree.body[i], ast.FunctionDef):
            defs.append(destination_tree.body[i])
            destination_tree.body.pop(i)
    defs = sorted(defs, key=lambda k: k.name)
    destination_tree.body.extend(defs)
    return destination_tree

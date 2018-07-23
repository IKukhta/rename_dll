#!/usr/bin/env python

import argparse
import subprocess
import re
import sys
import os
import shutil


def rename_dll(inputdll, outputdll, libpath, env):
    find_tool('link', env)
    find_tool('dumpbin', env)

    # dump the dll exports using dumpbin
    print "Dumping {}".format(inputdll)
    out = subprocess.check_output([
        'dumpbin', 
        '/EXPORTS', inputdll
        ], 
        env = env, shell=True)

    # get all the function definitions
    print "Renaming library in DEF file"
    lines = out.split('\n')
    pattern = r'^\s*(\d+)\s+[A-Z0-9]+\s+[A-Z0-9]{8}\s+([^ ]+)'

    library_output = 'EXPORTS \n'

    for line in lines:
        matches = re.search(pattern, line)

        if matches is not None:
            #ordinal = matches.group(1)
            function_name = matches.group(2)
            library_output = library_output + function_name + '\n'

    # write the def file
    deffile_name = outputdll[:-4] + '.def'
    with open(deffile_name, 'w') as f:
        f.write(library_output)

    print "Linking with new name: {}".format(deffile_name)
    out = subprocess.check_output([
        'lib', 
        '/DEF:' + deffile_name,
        ], 
        env = env, 
        cwd = libpath,
        shell=True)

    print 'Remove .def file'
    os.remove(deffile_name)


def find_tool(name, env):
    print '{}:'.format(name)
    if subprocess.call(['where', name], env=env) != 0:
        print 'Please make sure that VS bin is in path, link.exe and dumpbin.exe should be in path!'
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Renames a dll file, generates new def and lib files')
    parser.add_argument('inputdll', help='input dll')
    parser.add_argument('outputdll', help='output dll')
    parser.add_argument('libpath', help='output .lib and .exp path')
    args = parser.parse_args()

    rename_dll(args.inputdll, args.outputdll, args.libpath, os.environ)

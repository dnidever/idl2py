#!/usr/bin/env python

"""IDL2PY.PY - Simple IDL to Python converter

"""

import os
import re

def datadir():
    """ Return the repo data directory."""
    fil = os.path.abspath(__file__)
    codedir = os.path.dirname(fil)
    datadir = codedir+'/data/'
    return datadir

def readfile(filename):
    # Load the file
    with open(filename,'r') as f:
        lines = f.readlines()
    return lines

def writefile(filename,lines):
    # Load the file
    with open(filename,'w') as f:
        f.writelines()

def sed_inplace(filename, pattern, repl):
    '''
    Perform the pure-Python equivalent of in-place `sed` substitution: e.g.,
    `sed -i -e 's/'${pattern}'/'${repl}' "${filename}"`.
    '''
    # For efficiency, precompile the passed regular expression.
    pattern_compiled = re.compile(pattern)

    # For portability, NamedTemporaryFile() defaults to mode "w+b" (i.e., binary
    # writing with updating). This is usually a good thing. In this case,
    # however, binary writing imposes non-trivial encoding constraints trivially
    # resolved by switching to text writing. Let's do that.
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        with open(filename) as src_file:
            for line in src_file:
                tmp_file.write(pattern_compiled.sub(repl, line))

    # Overwrite the original file with the munged temporary file in a
    # manner preserving file attributes (e.g., permissions).
    shutil.copystat(filename, tmp_file.name)
    shutil.move(tmp_file.name, filename)


def sed(pattern,repl,line):
    """ sed-like function """

    # For efficiency, precompile the passed regular expression.
    #pattern_compiled = re.compile(pattern)
    #newline = pattern_compiled.sub(repl, line)
    
    newline = re.sub(pattern,repl, line)
    
    return newline
    
def convert(filename):
    """
    Convert an IDL file to Python
    """

    if os.path.exists(filename)==False:
        raise ValueError(filename,' NOT FOUND')
    
    # Load the file
    lines = readfile(filename)
    # make it a single line
    line = ' '.join(lines)
    
    # Load the search/replace values
    replace = readfile(datadir()+'idl2py_sed.txt')
    # remove comment lines
    replace = [r for r in replace if r[0]!='#']
    replace = [r[0:-1] if r.endswith('\n') else r for r in replace]
    # Break the statement up into pattern and replacement
    pattern,repl = [],[]
    for i in range(len(replace)):
        dum = replace[i].split('/')
        if len(dum)==4:
            pattern.append(dum[1])
            repl.append(dum[2])        
    
    # Do the search/replace
    for i in range(len(replace)):
        print(i,pattern[i],repl[i])
        line = sed(pattern[i],repl[i],line)
    
    # Add import statements at the beginning
    
    # continue line $
    # comment blocks at beginning of program
    # stop


    # Write to new file
    fdir = os.path.dirname(filename)
    base = os.path.basename(filename)
    if base[-4:]=='.pro':
        newbase = base[0:-4]+'.py'
    else:
        newbase = base+'.py'
    newfile = fdir+'/'+newbase
    import pdb; pdb.set_trace()    
    writefile(newfile,line)
        
    
    import pdb; pdb.set_trace()

#!/usr/bin/env python

"""IDL2PY.PY - Simple IDL to Python converter

"""

import os
import re
import numpy as np

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
        f.writelines(lines)

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

    newline = re.sub(pattern,repl, line, flags=re.IGNORECASE)

    return newline

def searchreplace(pattern,repl,lines,verbose=False):
    # Do the search+replace

    newlines = []
    for i,line in enumerate(lines):
        oline = line
        # Remove comment first
        if '#' in line:
            comment = line[line.find('#'):]
            line = line[0:line.find('#')]
        else:
            comment = None
        # Do the search/replace with sed
        for j in range(len(pattern)):
            line = sed(pattern[j],repl[j],line)
        # Add comment line back
        if comment is not None:
            line += comment
        # Do not add lines that had something and now don't
        # e.g. endfor line
        if len(oline.strip())>0 and len(line.strip())==0:
            continue
        else:
            newlines.append(line)
        if verbose:
            print(i+1,oline,'  ->  ',line)

    return newlines
            
def fixcomments(lines):
    # Fix comments in lines
    newlines = []
    for i,l in enumerate(lines):
        if ';;' in l:
            comment = l[l.find(';;')+2:]
            newl = [l[0:l.find(';;')]+'#'+comment]
        elif ';' in l:
            comment = l[l.find(';')+1:]
            newl = [l[0:l.find(';')]+'#'+comment]            
        else:
            newl = [l]
        newlines += newl

    return newlines
        
def fixifthen(lines):
    # Fix if/then/else on the same line
    newlines = []
    for i,l in enumerate(lines):
        ol = l  # original
        # strip off comments at end
        if '#' in l:
            comment = l[l.find('#'):]
            l = l[0:l.find('#')]
            l = l.strip()    # remove extra whitespace
        else:
            comment = None
        ll = l.lower().strip()            
        words = ll.split(' ')
        nif = np.sum(np.array(words)=='if')
        nthen = np.sum(np.array(words)=='then')
        nbegin = np.sum(np.array(words)=='begin')
        nelse = np.sum(np.array(words)=='else')
        if nif>1 and nthen>0:
            #print(i,'fixing multiple ifs')
            # if ... then if ... then ...
            if nthen==2 and nbegin==0 and nelse==0:
                # break into three lines
                dum = re.split('then', l, flags=re.IGNORECASE)
                newl = [dum[0]+' then begin','  '+dum[1]+' then begin','    '+dum[2],'  endif','endif']

            # if ... then if ... then begin            
            elif nthen==2 and nbegin==1 and nelse==0:
                # break into three lines
                dum = re.split('then', l, flags=re.IGNORECASE)
                newl = [dum[0]+' then begin','  '+dum[1]+' then begin']
                # THIS ONE HAS PROBLEMS BECAUSE WE NEED AN EXTRA ENDIF AT THE END
                print('WE NEED AN EXTRA ENDIF AT THE END OF THIS BLOCK!!!')
                
            # if ... then if ... then ... else ...
            elif nthen==2 and nelse==1 and nbegin==0:
                # break into three lines
                dum = re.split('then', l, flags=re.IGNORECASE)
                dum2 = re.split('else', dum[2], flags=re.IGNORECASE)                
                newl = [dum[0]+' then begin','  '+dum[1]+' then begin','    '+dum2[0],'  endif else begin','    '+dum2[1],'  endelse','endif']
            
            # if ... then if ... then ... else begin
            elif nthen==2 and nelse==1 and nbegin==1:
                # break into three lines
                dum = re.split('then', l, flags=re.IGNORECASE)
                dum2 = re.split('else', dum[2], flags=re.IGNORECASE)                
                newl = [dum[0]+' then begin','  '+dum[1]+' then begin','    '+dum2[0],'  endif else begin']
                newlines += newl
                # THIS ONE HAS PROBLEMS BECAUSE WE NEED AN EXTRA ENDIF AT THE END                
                print('WE NEED AN EXTRA ENDIF AT THE END OF THIS BLOCK!!!')
                
            #print('multiple ifs')
            #import pdb; pdb.set_trace()
        elif ll.startswith('if') and nthen>0 and nelse>0:
            #print(i,'fix if/then/else')
            dum = re.split('then',l,flags=re.IGNORECASE)
            dum2 = re.split('else',dum[1],flags=re.IGNORECASE)
            if len(dum2)<2:
                print('problem fixing '+l)
                newl = [l]
            else:
                newl = [dum[0]+'then begin','  '+dum2[0],'endif else begin','  '+dum2[1],'endelse']            
            #import pdb; pdb.set_trace()
        elif ll.startswith('if') and 'then' in ll and ll.endswith('begin')==False:
            #print(i,'fix if/then')
            dum = l.split('then')
            newl = [dum[0]+' then begin','  '+dum[1],'endif']
        else:
            newl = [l]
        # Add coment at end
        if comment is not None:
            newl[0] += comment
            
        newlines += newl
            
    return newlines

def fixfordo(lines):
    # Fix for/do on the same line
    newlines = []
    for i,l in enumerate(lines):
        ol = l
        # strip off comments at end
        if '#' in l:
            comment = l[l.find('#'):]
            l = l[0:l.find('#')]
            l = l.strip()  # remove extra whitespace
        else:
            comment = None
        ll = l.lower().strip()
        words = ll.split(' ')
        nfor = np.sum(np.array(words)=='if ')
        ndo = np.sum(np.array(words)=='do')
        nbegin = np.sum(np.array(words)=='begin')
        if ll.startswith('for') and ndo>0:
            #print(i,'fix for/do')
            dum = re.split('do',l,flags=re.IGNORECASE)
            newl = [dum[0]+'do begin','  '+dum[1],'endfor']
        else:
            newl = [l]

        # Add coment at end
        if comment is not None:
            newl[0] += comment

        newlines += newl            
            
    return newlines
    
def fixindent(lines):
    """ Fix indents in IDL program lines."""
    # Loop over the IDL lines and fix the indents
    # figure out the indent level
    level = 0
    uptype = []
    dwntype = []
    indentlevel = np.zeros(len(lines),int)
    for i,l in enumerate(lines):
        #print(i,level)
        up = False
        dwn = False
        ll = l.lower().strip()
        l = l.strip()
        indentlevel[i] = level
        # Set the indent
        lines[i] = level*'    '+l
        # Increase indent
        for u in ['pro ','function ','if ','for ','while ','case ','else ']:
            if (u != 'else ' and ll.startswith(u)) or (u=='else ' and u in ll):
                up = True
                uptype.append(u)
                level += 1
                #print('up ',u)
        # Decrease indent
        #if up==False:
        for d in ['endif','endelse','endfor','endwhile','endcase','end']:
            if ll.startswith(d):
                dwn = True
                dwntype.append(d)
                level -= 1
                #print('down ',d)
                break
        # Up AND Down, e.g. "endif else begin", this is actually a DOWN
        if up and dwn:
            indentlevel[i] = level-1
        # If down, then set the indent at the new level
        if dwn:
            lines[i] = (level-1)*'    '+l            
            
    return lines

def fixfor(lines):
    """ Fix for loops. """

    for i,l in enumerate(lines):
        ll = l.lower().strip()
        words = ll.split(' ')
        if ll.startswith('for'):
            #print('for',ll)
            # for i=0,nfiles-1 do begin
            ind0 = re.search('for',l,flags=re.IGNORECASE).start()
            ind1 = re.search('for',l,flags=re.IGNORECASE).end()+1
            ind2 = l.find('=')
            ind3 = l.find(',')
            ind4 = re.search('do',l,flags=re.IGNORECASE).start()-1
            var = l[ind1:ind2]
            start = l[ind2+1:ind3]
            stop = l[ind3+1:ind4]
            if stop[-2:]=='-1':
                stop = stop[0:-2]
            else:
                stop = stop+'+1'
            if start=='0':
                newl = ind0*' ' + 'for '+var+' in range('+stop+')'+l[ind4:]                
            else:
                newl = ind0*' ' + 'for '+var+' in np.arange('+start+','+stop+')'+l[ind4:]
            lines[i] = newl
            
    return lines

def convert(filename):
    """
    Convert an IDL file to Python
    """

    if os.path.exists(filename)==False:
        raise ValueError(filename,' NOT FOUND')
    
    # Load the file
    lines = readfile(filename)

    # Fix the continuation lines, add the lines together
    for i,l in enumerate(lines):
        ll = l.lower().rstrip().rstrip('\n')
        if ll.endswith('$'):
            lines[i] = l.rstrip('\n')[:-1]  # remove newline and $
    # Now join and split on newline again
    line = ''.join(lines)
    lines = line.split('\n')
    ## Strip newline at end
    #lines = [l.rstrip('\n') if l.endswith('\n') else l for l in lines]

    # Fix comments
    lines = fixcomments(lines)
    
    # Fix if/then/else on same lines
    lines = fixifthen(lines)

    # Fix for/do on same line
    lines = fixfordo(lines)
    
    # Fix indents
    lines = fixindent(lines)

    # Fix for statements
    lines = fixfor(lines)

    # Load the search/replace values
    replace = readfile(datadir()+'idl2py_sed.txt')
    # remove comment lines in file
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
    lines = searchreplace(pattern,repl,lines)
        
    # Make it a single line
    line = ' \n'.join(lines)
            
    # Add import statements at the beginning
    beg = '#!/usr/bin/env python\n\n'
    beg += 'import os\nimport time\nimport numpy as np\n\n'
    line = beg+line

    # Other things to add:
    # -comment blocks at beginning of program
    # -file_delete, check for /allow
    # -strtrim, remove ,2) as well
    # -mean/total with /nan, convert to np.nanmean,np.nansum, etc.
    # -fits_read, mrdfits
    # -sxpar, sxaddpar, sxdelpar
    # -parentheses and : in pro/function line
    # -closing ) at end of print statements
    # -keyword_set
    # -np.where(), number of returned indices
    # -sort, reverse, uniq
    # -file_copy

    # Write to new file
    fdir = os.path.dirname(filename)
    if fdir=='': fdir='.'
    base = os.path.basename(filename)
    if base[-4:]=='.pro':
        newbase = base[0:-4]+'.py'
    else:
        newbase = base+'.py'
    newfile = fdir+'/'+newbase
    #print('Writing to ',newfile)
    writefile(newfile,line)
        

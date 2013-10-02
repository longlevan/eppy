# Copyright (c) 2012 Santosh Philip

# This file is part of eppy.

# Eppy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Eppy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with eppy.  If not, see <http://www.gnu.org/licenses/>.


"""sub class bunch in steps going from data, aliases, functions"""
# TODO : go thru with a fine tooth comb. make unit tests

import sys
from EPlusInterfaceFunctions import readidf
from bunch import *
import bunchhelpers

class BadEPFieldError(Exception):
    pass

class RangeError(Exception):
    pass
    

def somevalues(dt):
    """returns some values"""
    return dt.Name, dt.Construction_Name, dt.obj
    
def extendlist(lst, i, value=''):
    """extend the list so that you have i-th value"""
    if i < len(lst):
        pass
    else:
        lst.extend([value, ] * (i - len(lst) + 1))

class EpBunch_1(Bunch):
    """Has data in bunch"""
    def __init__(self, obj, objls, objidd, *args, **kwargs):
        super(EpBunch_1, self).__init__(*args, **kwargs)
        self.obj = obj
        self.objls = objls
        self.fieldnames = self.objls # just an alias
        self.objidd = objidd
    def __setattr__(self, name, value):
        if name in ('obj', 'objls', 'fieldnames', 'objidd'):
            super(EpBunch_1, self).__setattr__(name, value)
            return None
        elif name in self['objls']:
            i = self['objls'].index(name)
            try:
                self['obj'][i] = value
            except IndexError, e:
                extendlist(self['obj'], i)
                self['obj'][i] = value
        else:
            s = "unable to find field %s" % (name, )
            raise BadEPFieldError(s)
    def __getattr__(self, name):
        if name in ('obj', 'objls', 'fieldnames', 'objidd'):
            return super(EpBunch_1, self).__getattr__(name)
        elif name in self['objls']:
            i = self['objls'].index(name)
            try:
                return self['obj'][i]
            except IndexError, e:
                return ''
        else:
            s = "unable to find field %s" % (name, )
            raise BadEPFieldError(s)
    def __repr__(self):
        """print this as an idf snippet"""
        lines = [str(val) for val in self.obj]
        comments = [comm.replace('_', ' ') for comm in self.objls]
        lines[0] = "%s," % (lines[0], ) # comma after first line
        for i, line in enumerate(lines[1:-1]):
            lines[i + 1] = '    %s,' % (line, ) # indent and comma
        lines[-1] = '    %s;' % (lines[-1], )# ';' after last line
        lines = [line.ljust(26) for line in lines] # ljsut the lines
        filler = '%s    !- %s'
        nlines = [filler % (line, comm) for line, 
            comm in zip(lines[1:], comments[1:])]# adds comments to line
        nlines.insert(0, lines[0])# first line without comment
        s = '\n'.join(nlines)
        return '\n%s\n' % (s, )

class EpBunch_2(EpBunch_1):
    """Has data, aliases in bunch"""
    def __init__(self, obj, objls, objidd, *args, **kwargs):
        super(EpBunch_2, self).__init__(obj, objls, objidd, *args, **kwargs)
    def __setattr__(self, name, value):
        if name == '__aliases':
            self[name] = value
            return None
        try:
            origname = self['__aliases'][name]
            super(EpBunch_2, self).__setattr__(origname, value)
        except KeyError, e:
            super(EpBunch_2, self).__setattr__(name, value)
    def __getattr__(self, name):
        if name == '__aliases':
            return super(EpBunch_2, self).__getattr__(name)
        try:
            origname = self['__aliases'][name]
            return super(EpBunch_2, self).__getattr__(origname)
        except KeyError, e:
            return super(EpBunch_2, self).__getattr__(name)
    
class EpBunch_3(EpBunch_2):
    """Has data, aliases, functions in bunch"""
    def __init__(self, obj, objls, objidd, *args, **kwargs):
        super(EpBunch_3, self).__init__(obj, objls, objidd, *args, **kwargs)
        self['__functions'] = {}
    def __setattr__(self, name, value):
        if name == '__functions':
            self[name] = value
            return None
        try:
            origname = self['__functions'][name]
            self[origname] = value
        except KeyError, e:
            super(EpBunch_3, self).__setattr__(name, value)
    def __getattr__(self, name):
        if name == '__functions':
            # return super(EpBunch_3, self).__getattr__(name)
            return self['__functions']
        try:
            func = self['__functions'][name]
            return func(self)
        except KeyError, e:
            return super(EpBunch_3, self).__getattr__(name)
            
class EpBunch_4(EpBunch_3):
    """h implements __getitem__ and __setitem__"""
    def __init__(self, obj, objls, objidd, *args, **kwargs):
        super(EpBunch_4, self).__init__(obj, objls, objidd, *args, **kwargs)
    def __getitem__(self, key):
        if key in ('obj', 'objls', 'fieldnames', 'objidd', '__functions', '__aliases'):
            return super(EpBunch_4, self).__getitem__(key)
        elif key in self['objls']:
            i = self['objls'].index(key)
            try:
                return self['obj'][i]
            except IndexError, e:
                return ''
        else:
            s = "unknown field %s" % (key, )
            raise BadEPFieldError(s)
    def __setitem__(self, key, value):
        if key in ('obj', 'objls', 'fieldnames', 'objidd', '__functions', '__aliases'):
            super(EpBunch_4, self).__setitem__(key, value)
            return None
        elif key in self['objls']:
            i = self['objls'].index(key)
            try:
                self['obj'][i] = value
            except IndexError, e:
                extendlist(self['obj'], i)
                self['obj'][i] = value
            
        else:
            s = "unknown field %s" % (key, )
            raise BadEPFieldError(s)
        

class EpBunch_5(EpBunch_4):
    """implements getrange, checkrange"""
    def __init__(self, obj, objls, objidd, *args, **kwargs):
        super(EpBunch_5, self).__init__(obj, objls, objidd, *args, **kwargs)
    def getrange(self, fieldname):
        """get the ranges for this field"""
        keys = ['maximum', 'minimum', 'maximum<', 'minimum>', 'type']
        index = self.objls.index(fieldname)
        fielddct = self.objidd[index]
        therange = {}
        for key in keys:
            therange[key] = fielddct.setdefault(key, None)
        if therange['type']:
            therange['type'] = therange['type'][0]
        if therange['type'] == 'real':
            for key in keys[:-1]:
                if therange[key]:
                    therange[key] = float(therange[key][0])
        if therange['type'] == 'integer':
            for key in keys[:-1]:
                if therange[key]:
                    therange[key] = int(therange[key][0])
        return therange
             
    def checkrange(self, fieldname):
        """throw exception if the out of range"""
        fieldvalue = self[fieldname]
        therange = self.getrange(fieldname)
        keys = ['maximum', 'minimum', 'maximum<', 'minimum>']
        index = self.objls.index(fieldname)
        # fielddct = self.objidd[index]
        if therange['maximum'] != None:
            if fieldvalue > therange['maximum']:
                s = "Value %s is not less or equal to the 'maximum' of %s"
                s = s % (fieldvalue, therange['maximum'])
                raise RangeError(s)
        if therange['minimum'] != None:
            if fieldvalue < therange['minimum']:
                s = "Value %s is not greater or equal to the 'minimum' of %s"
                s = s % (fieldvalue, therange['minimum'])
                raise RangeError(s)
        if therange['maximum<'] != None:
            if fieldvalue >= therange['maximum<']:
                s = "Value %s is not less than the 'maximum<' of %s"
                s = s % (fieldvalue, therange['maximum<'])
                raise RangeError(s)
        if  therange['minimum>'] != None:
            if fieldvalue <= therange['minimum>']:
                s = "Value %s is not greater than the 'minimum>' of %s"
                s = s % (fieldvalue, therange['minimum>'])
                raise RangeError(s)
        return fieldvalue
        
EpBunch = EpBunch_5

def main():

    # read code
    # iddfile = "../iddfiles/Energy+V6_0.idd"
    iddfile = "./walls.idd"
    fname = "./walls.idf" # small file with only surfaces
    data, commdct = readidf.readdatacommdct(fname, iddfile=iddfile)

    # setup code walls - can be generic for any object
    dt = data.dt
    dtls = data.dtls
    wall_i = dtls.index('BuildingSurface:Detailed'.upper())
    wallkey = 'BuildingSurface:Detailed'.upper()

    dwalls = dt[wallkey]
    dwall = dwalls[0]

    wallfields = [comm.get('field') for comm in commdct[wall_i]]
    wallfields[0] = ['key']
    wallfields = [field[0] for field in wallfields]
    wall_fields = [bunchhelpers.makefieldname(field) for field in wallfields]
    print wall_fields[:20]

    bwall = EpBunch(dwall, wall_fields)

    print bwall.Name
    print data.dt[wallkey][0][1]
    bwall.Name = 'Gumby'
    print bwall.Name
    print data.dt[wallkey][0][1]
    print

    # set aliases
    bwall.__aliases = {'Constr':'Construction_Name'} 

    print "wall.Construction_Name = %s" % (bwall.Construction_Name, )
    print "wall.Constr = %s" % (bwall.Constr, )
    print
    print "change wall.Constr"
    bwall.Constr = 'AnewConstr'
    print "wall.Constr = %s" % (bwall.Constr, )
    print "wall.Constr = %s" % (data.dt[wallkey][0][3], )
    print

    # add functions
    bwall.__functions = {'svalues':somevalues} 

    print bwall.svalues
    print bwall.__functions



if __name__ == '__main__':
    main()


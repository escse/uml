import os
import re
import sys

def capture(pattern):
    return r"({})".format(pattern)

def non_capture(pattern):
    return r"(?:{})".format(pattern)

def one(pattern):
    return r"(?:{}\s*)?".format(pattern)

def any(pattern):
    return r"(?:{}\s*)*".format(pattern)

def non(pattern):
    return r"[^{}]".format(pattern)

def parentheses(pattern):
    return r"\(\s*{}\s*\)".format(pattern)

public = r"public\s+"
class_ = r"(?:class|enum|interface)\s+"
extends = r"extends\s+"
implements = r"implements\s+"
capture_name = r"(\w+)\s+"

name = r"\w+"
comma = r"\s*,\s*"


# pattern_private_class = "\s*".join([public, class_, capture_name, any(extends + capture_name), one(implements + capture(name + any(comma + name))), "\{(.+)\}"])
# private_classes = re.compile(pattern_private_class, re.S).findall(files)


class Method(object):

    def __init__(self, control, return_type, name, parameter_types):
        self.control = control
        self.name = name
        self.parameter_types = ", ".join(parameter_types)
        self.return_type = return_type
        self.sign = "+" if "public" in self.control else ""
        
    def __str__(self):
        return " ".join([self.sign, self.name , "(" + self.parameter_types + ")", ":", self.return_type])

class Variable(object):

    def __init__(self, control, type_, name):
        self.control = control
        self.type = type_
        self.name = name
        self.sign = "+" if "public" in self.control else ""
        

    def __str__(self):
        return " ".join([self.sign, self.name, ":", self.type])

class UML(object):

    def __init__(self, filename):
        with open(filename, "r") as f:
            source_code = f.read()
        # parse class
        pattern_public_class = "".join([public, class_, r"(\w+)\s*", one(extends + r"(\w+)\s*"), one(implements + capture(name + any(comma + name))), "\{(.+)\}"]) #"\{(.+(?!class))\}       
        public_class = re.compile(pattern_public_class, re.S).findall(source_code)
        if not public_class:
            print filename
            return
        class_name, parent_name, interface, code = public_class[0]
        self.class_name = class_name.strip()
        self.parent_name = parent_name.strip()
        self.intefaces = [i.strip() for i in interface.split(",")] if interface else []
        code = code.strip()
        # parse methods
        control = r"(?:public\s+|private\s+|protected\s+|)"
        static = r"(?:static\s+|)"
        final = r"(?:final\s+|)"
        control_capture = capture("|".join([control+static+final, control+final+static, final+control+static, final+static+control, static+final+control, static+control+final]))
        parameter = r"\w+\s+\w+"
        parameters = one(capture(parameter + any(comma + parameter)))
        pattern_methods = "".join([control_capture, r"(\w*\s+|)(\w+)\s*",  parentheses(parameters)])
        methods = re.compile(pattern_methods, re.S).findall(code)
        self.methods = []
        for ctrol_, type_, name_, para_ in methods:
            c = " ".join(sorted(ctrol_.split()))
            if para_:
                para_ = para_.split(",")
                p = [pp.split()[0] for pp in para_]
            else:
                p = []
            self.methods.append(Method(c, type_, name_, p))
        # parse variables
        pattern_variables = "".join([control_capture, capture_name, "(\w+)\s*", "(?:=|;)"])
        variables = re.compile(pattern_variables, re.S).findall(code)
        self.variables = []
        for ctrol_, type_, name_ in variables:
            c = " ".join(sorted(ctrol_.split()))
            self.variables.append(Variable(c, type_, name_))
    
    def __str__(self):
        name = self.class_name
        variables = "\\l".join(str(c).strip() for c in self.variables if c.sign)
        methods = "\\l".join(str(c).strip() for c in self.methods if c.sign)
        supers = self.intefaces[:]
        if self.parent_name:
            supers.insert(0, self.parent_name)
        hierarchy = "\n\t".join(self.class_name + " -> " + c for c in supers)
        res = "\t" + name + " [\t\tlabel = \"{" + name + "|" + variables + "|" + methods + "}\"\t]\t" + hierarchy 
        return res



def findFileType(dir, filetype):
    L = []
    for root, dirs, files in os.walk(dir):  
        for file in files:
            if filetype in os.path.splitext(file)[1]:  
                L.append(os.path.join(root, file))  
    return L  

# UML("p.java")

template = """
digraph G {{
    fontname = "Courier New"
    fontsize = 8

    node [
            fontname = "Courier New"
            fontsize = 8
            shape = "record"
    ]

    edge [
            fontname = "Courier New"
            fontsize = 8
    ]
    {}
}}
"""

def main():
    
    if len(sys.argv) == 1:
        dir = "."
    else:
        dir = sys.argv[1]
    files = findFileType(dir, "java")
    umls = [UML(filename) for filename in files]
    uml_text = "\n".join(str(c) for c in umls)
    graph_text = template.format(uml_text)
    with open("graph.gv", "w") as f:
        f.write(graph_text)

if __name__ == "__main__":
    main()
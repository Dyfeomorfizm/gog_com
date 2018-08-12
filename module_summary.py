import sys

def get_first_paragraph(text):
    paragraphs = text.split("\n\n")
    return paragraphs[0]

def do_import(module_name):
    module = __import__(module_name)
    return module

def create_doc(module):
    doc = module.__name__ + "\n" + get_first_paragraph(module.__doc__)
    for m in dir(module):
        struct = getattr(module, m)
        try:
            name = struct.__name__
            doc += "\n----------------\n"
            doc += name + "\n" + get_first_paragraph(str(struct.__doc__))
        except Exception as e:
            print(e)
    return doc

def to_file(filename, doc):
    with open(filename, 'w') as f:
        f.write(doc)

def main(module_name, filename):
    to_file(filename, create_doc(do_import(module_name)))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
    

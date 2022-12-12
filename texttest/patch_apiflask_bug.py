
import os

def find_site_packages(root):
    for r, dirs, files in os.walk(os.path.join(root, "venv")):
        if "site-packages" in dirs:
            return os.path.join(r, "site-packages")

def find_file_to_edit():
    root = os.path.dirname(os.path.dirname(__file__))
    site_packages = find_site_packages(root)
    for r, _, files in os.walk(site_packages):
        for fn in files:
            if fn.endswith(".py") and r.lower().endswith("apiflask"):
                path = os.path.join(r, fn)
                with open(path) as f:
                    for line in f:
                        if "SWAGGER_UI_CONFIG" in line and not line.startswith("SWAGGER_UI_CONFIG"):
                            return path

def patch_file(fn):
    fromText = "= userConfig[attr]"
    toText = "= eval(userConfig[attr])"
    newFn = fn + ".new"
    with open(newFn, "w") as wf:
        with open(fn) as f:
            for line in f:
                if fromText in line:
                    wf.write(line.replace(fromText, toText))
                else:
                    wf.write(line)
    os.remove(fn)
    os.rename(newFn, fn)

if __name__ == '__main__':
    # see https://github.com/apiflask/apiflask/issues/381
    fn = find_file_to_edit()
    print("Patching file", fn)
    patch_file(fn)
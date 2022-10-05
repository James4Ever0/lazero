import sys
import os

os.chdir("../")
sys.path.insert(0, ".")  # you should use 'prepend' instead of 'append'
# sys.path.insert(0,"/root/Desktop/works/pyjom/symlinks/lazero/") # you should use 'prepend' instead of 'append'
# ignore the global proxy now, we are not going to use that.
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""

import sys
import os

project_root = os.getcwd()

if os.path.exists(project_root):
    sys.path.append(project_root)
#-*- encoding: utf8 -*-
from pathlib import Path
import os
import sys

# working directory 얻기
workingdir = os.path.abspath(os.path.dirname(__file__))
parentdir = Path(workingdir).parent
sys.path.append(parentdir)
print('Parent dir: ', parentdir)

#from parentdir import common
from common import account
print(account)


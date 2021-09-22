import os
import sys
path = os.path.dirname(__file__)
pythonPath = path.split('melScript')[0]
if not pythonPath in sys.path:
    sys.path.append(pythonPath)
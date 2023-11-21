import sys
import os
currentPath = os.path.dirname(__file__)
if sys.version.startswith('3'):
    pythonPath = os.path.join(currentPath, 'py3')
    sys.path.append(pythonPath)
else:
    pythonPath = os.path.join(currentPath, 'py2')
    sys.path.append(pythonPath)

def main():
    import springmagic
    springmagic.main()
import os
import sys
path = os.path.dirname(__file__)
print(path)
sysPath = ''
if sys.version.startswith('2'):
    sysPath = os.path.join(path,'py2')

if sys.version.startswith('3'):
    sysPath = os.path.join(path,'py3')

if not sysPath in sys.path:
    sys.path.append(sysPath)
    
def main(*args, **kwargs):
    if sysPath.endswith('3'):
        print('3')
        from springmagic import py3
        py3.main()
    if sysPath.endswith('2'):
        print('2')
        from springmagic import py2
        
        py2.main()
    return
if __name__ == "__main__":
    with springmagic.app():
        springmagic.main()
    

    

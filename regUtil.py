#-*- coding:utf-8 -*-
import ctypes
import sys
import os

try:
    import _winreg  as reg
except ImportError:
    import winreg as reg
    
def check_env(key):
    ret = True
    runkey = reg.OpenKey(reg.HKEY_CURRENT_USER,
        r"Environment", 0, reg.KEY_READ)
    try:
        print(reg.QueryValueEx(runkey, key))
    except:
        ret = False
    reg.CloseKey(runkey)

    return ret 
def getEnv(name):
    try:
        registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, 'Environment', 0,
                                       reg.KEY_READ)
        value, regtype = reg.QueryValueEx(registry_key, name)
        reg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None
# def read_registry(key, valueex):
#     reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_READ)
#     value = reg.QueryValueEx(reg_key, valueex)
#     reg_key.Close()
#     return value
# 레지스트리통해 영구적으로 환경변수를 추가합니다.
def setEnv(name, value):
    try:
        reg.CreateKey(reg.HKEY_CURRENT_USER, 'Environment')
        registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, 'Environment', 0, 
                                       reg.KEY_WRITE)
        reg.SetValueEx(registry_key, name, 0, reg.REG_SZ, value)
        reg.CloseKey(registry_key)
        return True
    except WindowsError:
        return False
# system 변수 추가 
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def getPythonPath(keyname = 'PYTHONPATH'):
    try:
        registry_key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                                        0,reg.KEY_READ)
        value, regtype = reg.QueryValueEx(registry_key, keyname)
        reg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None

def appendPath(value,type=reg.REG_EXPAND_SZ,keyname='PYTHONPATH'):
    if is_admin():
        regRoot = reg.ConnectRegistry(None,reg.HKEY_LOCAL_MACHINE)
        subDir=r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
        
        key_read=reg.OpenKey(regRoot,subDir)
        count = reg.QueryInfoKey(key_read)[1]
        for i in range(count):
            name,values,type_ = reg.EnumValue(key_read,i)
            if name.lower() == keyname.lower():
                if values[-1] == ';':
                    values += value
                else:
                    values += ';{0}'.format(value)
                key_write = reg.OpenKey(regRoot,subDir,0,reg.KEY_WRITE)
                
                reg.SetValueEx(key_write,name,0,type,values)
                reg.CloseKey(key_write)
        reg.CloseKey(key_read)
    else:
        if sys.version_info[0] == 3:
            ctypes.windll.shell32.ShellExecuteW(None,"runas",sys.executable,__file__,None,1)

def registry_key(key, subkey, value):
    """
    Create a new Windows Registry Key in HKEY_CURRENT_USER

    `Required`
    :param str key:         primary registry key name
    :param str subkey:      registry key sub-key name
    :param str value:       registry key sub-key value

    Returns True if successful, otherwise False

    """
    try:
        
        reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_WRITE)
        reg.SetValueEx(reg_key, subkey, 0, reg.REG_SZ, value)
        reg.CloseKey(reg_key)
        return True
    except Exception as e:
        print(e)
        return False 
# Get environment value from read_registry   
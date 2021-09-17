#-*- coding:utf-8 -*-
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
    
# Get environment value from read_registry
# Ex:(u'N:\\b1Env\\maya\\scripts;N:\\sccEnv\\scripts\\mGearScripts;N:\\', 1)

    
    
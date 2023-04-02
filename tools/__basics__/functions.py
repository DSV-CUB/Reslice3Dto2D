import os


def check_class_has_method(obj, method_name):
    return hasattr(obj, method_name) and type(getattr(obj, method_name)) == types.MethodType


def save_dcm(dcm, path, overwrite=False):
    name = ''.join(e for e in str(dcm[0x0010, 0x0010].value) if e.isalnum())
    seriesnumber = str(dcm[0x0020, 0x0011].value).zfill(4)
    serieddescription = ''.join(e for e in str(dcm[0x0008, 0x103E].value) if e.isalnum())
    uid = str(dcm[0x0008, 0x0018].value)

    dir_path = os.path.join(path, name, seriesnumber + "_" + serieddescription)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, uid + ".dcm")
    if not overwrite and os.path.isfile(file_path):
        pass
    else:
        dcm.save_as(file_path)
    return dir_path
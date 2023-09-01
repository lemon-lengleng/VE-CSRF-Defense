
"""
    Unpacking a Chrome extension and modify to security extension.
"""

import os
import json
import logging
import fnmatch
import hashlib
import argparse
import shutil
from urllib.parse import urljoin
from zipfile import ZipFile
from bs4 import BeautifulSoup


SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))

def read_from_zip(zf, filename):
    """ Returns the bytes of the file filename in the archive zf. """

    filename = filename.lstrip("./").split("?")[0]

    try:
        return zf.read(filename)

    except KeyError:
        # Now try lowercase
        mapping = {}
        for zi in zf.infolist():
            mapping[zi.filename.lower()] = zi.filename
        if filename.lower() in mapping:
            return zf.read(mapping[filename.lower()])
        logging.exception(zf.filename, filename, 'KeyError')
        return b''

    except Exception as e:
        logging.exception(zf.filename, filename, e)
        return b''


def beautify_script(content, suffix):
    """ Beautifies a script with js-beautify (https://www.npmjs.com/package/js-beautify). """

    filehash = hashlib.md5(content.encode()).hexdigest()
    temp_file = "/tmp/%s_%s" % (filehash, suffix.replace("/", "_"))

    with open(temp_file, "w") as fh:
        fh.write(content)
    os.system("js-beautify -t -r %s > /dev/null" % temp_file)

    with open(temp_file, "r") as fh:
        content = fh.read()
    os.unlink(temp_file)

    return content

def write_inline(x):
    fs = open("popup_inlinejs.txt", "a")   #popup行内js的内容
    fs.write(x+'\n')
    fs.close()
    return

def write(x):
    fs = open("results_themes.txt", "a")   #results_Exp.txt是批量分析结果
    fs.write(x+'\n')
    fs.close()
    return

def write_popjs(x):
    fs = open("popjs_secondCreate.txt", "a")   #results_Exp.txt是批量分析结果
    fs.write(x+'\n')
    fs.close()
    return

def Mod_background_v2(data,dest):
    print(data)
    if "background" in data:
        if "scripts" in data["background"]:
            data["background"]["scripts"].insert(0, "a.js") #√，请注意，使用 insert 方法可能会改变列表中其他元素的索引位置。如果列表中已经存在 "a.js"，那么使用 insert 方法会将其移动到最前面。如果您希望保持列表中元素的原始顺序，并仅在列表中不存在 "a.js" 的情况下添加到最前面，可以使用条件语句进行判断。
        elif "page" in data["background"]:
            print(data["background"]["page"])
            print(data["background"]["page"][0])
            html_path = os.path.join(dest,data["background"]["page"][0])
            print(html_path)
            # 读取原始的 HTML 文件内容
            with open(html_path, 'r') as file:
                html_content = file.read()
            # 在 head 标签中添加 JavaScript 引用
            js_code = '<script src="a.js"></script>'
            index = html_content.find('<head>')  # 查找第一个出现的位置
            new_text = html_content[:index+6] + js_code + html_content[index + 6:]
                # 将修改后的内容写入到新的 HTML 文件中
            with open(html_path, 'w') as file:
                file.write(new_text)
        else:
            data["background"]["scripts"] = ["a.js"]
    else:
        data["background"] = {"scripts":["a.js"]}
        print(data)

def Mod_background_v3(data,dest):
    if "background" in data:
        if "service_worker" in data["background"]:
            if "html" in data["background"]["service_worker"][0]:
                html_path = os.path.join(dest, data["background"]["service_worker"][0])
                # 读取原始的 HTML 文件内容
                with open(html_path, 'r') as file:
                    html_content = file.read()
                # 在 head 标签中添加 JavaScript 引用
                js_code = '<script src="a.js"></script>'
                index = html_content.find('<head>')  # 查找第一个出现的位置
                new_text = html_content[:index+6] + js_code + html_content[index + 6:]
                # 将修改后的内容写入到新的 HTML 文件中
                with open(html_path, 'w') as file:
                    file.write(new_text)
            else:
                data["background"]["service_worker"].insert(0,"a.js")  # 请注意，使用 insert 方法可能会改变列表中其他元素的索引位置。如果列表中已经存在 "a.js"，那么使用 insert 方法会将其移动到最前面。如果您希望保持列表中元素的原始顺序，并仅在列表中不存在 "a.js" 的情况下添加到最前面，可以使用条件语句进行判断。

        else:
            data["background"]["service_worker"] = ["a.js"]
    else:
        data["background"] = {"service_worker":["a.js"]}

def folder_to_zip(folderpath, zipath):  #压缩文件夹
    """
    folderpath : 待压缩文件夹的路径
    zipath     ：压缩后文件存放的路径
    """
    zip = ZipFile(zipath, "w", ZipFile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(folderpath):
        # 将待压缩文件夹下的所有文件逐一添加到压缩文件
        fpath = path.replace(os.path.dirname(folderpath), '')
        for filename in filenames:
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip.close()

def Auto_mod_Extensions(extension_crx):  #自动修改扩展
    #Auto_mod_Extensions
    extension_id = extension_crx.split("/")[5]
    dest = os.path.join(SRC_PATH.split("/src")[0],"Auto_moded_Extensions",extension_id)
    with ZipFile(extension_crx, 'r') as archive:   #解压
        archive.extractall(dest)
    manifest = os.path.join(dest,"manifest.json")
    with open(manifest, 'r', encoding='utf-8') as f:
        json_data = f.read()
    data = json.loads(json_data)    #manifest.json的对象
    print(data);
    #判断manifest版本号，对background修改有影响
    manifest_version = data["manifest_version"]
    if manifest_version not in (2, 3):
        logging.error('Only unpacking extensions with manifest version 2 or 3')
        # Considering only extensions with manifest versions 2 or 3
        return
    #对所需权限的修改
    required_permissions = ["tabs", "webRequest", "webRequestBlocking"]
    if "permissions" in data:   #处理权限
        for permission in required_permissions:
            if permission not in data["permissions"]:
                data["permissions"].append(permission)
    else:
        data["permissions"] = required_permissions
    print(data)
    #对background的修改
    if manifest_version == 2:
        print("222");
        Mod_background_v2(data,dest)
        print(data)
    else:
        Mod_background_v3(data,dest)
    #将data覆盖manifest.json
    with open(manifest, 'w') as file:
        json.dump(data,file,indent=6)
    #将a.js(扩展同源文件)加入目录中
    source_file = os.path.join(SRC_PATH, "扩展同源.js")
    target_directory = os.path.join(dest, "扩展同源.js")
    shutil.copy(source_file, target_directory)
    zip_name = shutil.make_archive(dest, 'zip', dest)
    directory,filename = os.path.split(zip_name)   #获取到文件目录、文件名
    #fliesion = os.splitext(filename)[0]    #去除后缀
    old_name, old_ext = os.path.splitext(filename) #
    new_filename = old_name + '.crx'
    new_filepath = os.path.join(directory, new_filename)    #构建新文件名
    os.rename(zip_name, new_filepath)
    shutil.rmtree(dest)
    os.mkdir(dest)
    shutil.move(new_filepath, dest) #将.zip文件移动到对应目录下
    print("加入扩展同源.js 打包")


def unpack_extension(extension_crx):    #提取压缩包中的文件

    extension_id = os.path.basename(extension_crx).split('.crx')[0] #获取文件名

    try:
        extension_zip = ZipFile(extension_crx)
        manifest = json.loads(read_from_zip(extension_zip, "manifest.json"))
        Auto_mod_Extensions(extension_crx)
    except:
        print("异常结束!")
        return

def extract_all(crx_path):
    """ Debug. """

    extension_zip = ZipFile(crx_path)
    extension_zip.extractall()


def unpack_all():   #解压缩文件夹中所有扩展
    path = os.path.join(SRC_PATH.split("/src")[0], 'Extensions_test')  # 填入解析文件夹
    EveryExtensionsDir = os.listdir(path)
    for everydir in EveryExtensionsDir:  # E->['0--2--piiophgglpmmlmmikaplnihikkfaadfc', '0--0--fippijmlifinjjpegmbgojkapopdoabk', '0--1--bajnmkinaopofbfaopenlfooloknfjlf']
        everyWholeDir = os.path.join(path, everydir)  # 获取每个扩展的完整路径
        firstPram = os.listdir(everyWholeDir)  # 获取每一个扩展里的文件名字f->['extension_3_7_0_0.crx']
        for crx in firstPram:  # 找.crx文件
            if '.crx' in crx:
                filepath = os.path.join(everyWholeDir, crx)  # 找到了每个扩展文件名.crx
                Extensions_input = os.path.join(SRC_PATH.split("/src")[0], 'Extensions_test_unpack', everydir)
                unpack_extension(filepath)  # .crx文件，目的文件
                # print(Extensions_input)
                # print("找到了crx",filepath)
                break
        # print(firstPram)
        return

if __name__ == "__main__":
    unpack_all()    #解压缩文件夹中所有扩展并修改将每个扩展进行安全修改


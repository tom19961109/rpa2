import yaml
from PyInstaller.__main__ import run
import sys
import uuid
import os
import shutil
from dotenv import load_dotenv


def gen_version_file(config):
    version_list = config['version'].split('.')
    version_file_info = f"""# UTF-8
#
# For more details about fixed properties, see:
# https://docs.python.org/3/library/sys.html#sys.version_info

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_list[0][1:]}, {version_list[1]}, {version_list[2]}, {version_list[3]}),
    prodvers=({version_list[0][1:]}, {version_list[1]}, {version_list[2]}, {version_list[3]}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0', [
        StringStruct(u'CompanyName', u'Tom'),
        StringStruct(u'FileDescription', u''),
        StringStruct(u'FileVersion', u'{version_list[0]}, {version_list[1]}, {version_list[2]}, {version_list[3]}'),
        StringStruct(u'InternalName', u''),
        StringStruct(u'LegalCopyright', u''),
        StringStruct(u'OriginalFilename', u'RPA.exe'),
        StringStruct(u'ProductName', u'RPA'),
        StringStruct(u'ProductVersion', u'{version_list[0]}, {version_list[1]}, {version_list[2]}, {version_list[3]}')
        ])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    with open("version_info.txt", "w", encoding="utf-8") as file:
        file.write(version_file_info)


sys.setrecursionlimit(50000)

if __name__ == '__main__':
    # load_dotenv('env/.env')
    with open("./config/config.yml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    gen_version_file(config)
    fast_mode = True

    if os.path.isdir('./dist'):
        shutil.rmtree('./dist')
        if not fast_mode:
            shutil.rmtree('./build')

    # '--name=大熊比較懶'

    file_name = 'MapleFreeStyle'
    opts = [
        'MapleFreeStyle.py',
        '-D',
        f'--name={file_name}',
        '--icon=./data/logo.ico',
        '--hidden-import=pywt._extensions._cwt',
        '--version-file=version_info.txt',
        # '--noconsole'
        '--uac-admin'
    ]

    run(opts)

    file_name = 'MapleFreeStyle' if not file_name else file_name
    shutil.copytree('./data', f'./dist/{file_name}/data')
    # shutil.copytree('./ui', f'./dist/{file_name}/ui')
    shutil.copytree('./config', f'./dist/{file_name}/config')
    shutil.copytree('./scripts', f'./dist/{file_name}/scripts')
    # shutil.copytree('./model', f'./dist/{file_name}/model')
    # shutil.copytree('./env', f'./dist/{file_name}/env')

    if os.path.isfile(f'./dist/{file_name}/config/config.json'):
        os.remove(f'./dist/{file_name}/config/config.json')

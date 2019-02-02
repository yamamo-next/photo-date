import os
import sys
import glob
import time
import datetime
import argparse

from PIL import Image
from PIL.ExifTags import TAGS

PSHELL = 'Set-ItemProperty "{0}" -name CreationTime -value "{1}"\n'

# ファイルの撮影日を取得
def get_orgdate_from_exif(file_path):
    img = Image.open(file_path)
    try:
        exif = {}
        for tag_id, value in img._getexif().items():
            tag = TAGS.get(tag_id, tag_id)
            exif[tag] = value
        return time.mktime(time.strptime(exif['DateTimeOriginal'],
                                         '%Y:%m:%d %H:%M:%S'))
    except Exception:
        return get_file_update(file_path)


# ファイルの更新日付を取得
def get_file_update(file_path):
    return os.stat(file_path).st_mtime    # 更新日時(modify time)


# ファイルの日付の更新と作成日付更新スクリプトの作成
def update_file_date(f, dir_path):
    files = glob.glob(os.path.join(dir_path, "*"))
    for file_path in files:
        if os.path.isdir(file_path) is True:
            update_file_date(f, file_path)
        else:
            _, ext = os.path.splitext(file_path)
            if ext.lower() == '.jpg':    # JPGファイルであればEXIF情報を取得
                new_date = get_orgdate_from_exif(file_path)
            else:
                new_date = get_file_update(file_path)
            os.utime(file_path, (new_date, new_date))    # 最終アクセス, 更新日時
            set_date = datetime.datetime.fromtimestamp(new_date)
            print("{0}: {1}".format(file_path, set_date))
            f.write(PSHELL.format(file_path, set_date))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='写真ファイルの日付を変更する')
    parser.add_argument('-d', '--data', default='photo', help='データフォルダ')
    parser.add_argument('-s', '--script', default='update.ps1', help='スクリプトファイル')

    args = parser.parse_args()
    if os.path.exists(args.data) is False:
        print("ファイルまたはフォルダを指定してください")
        sys.exit(1)

    with open(args.script, 'w') as f:
        update_file_date(f, args.data)

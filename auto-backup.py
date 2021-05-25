import json
import os
import hashlib
import platform
import shutil
import time


def md5sum(filename: str) -> str:
    def read_chunks(fp):
        fp.seek(0)
        chunk = fp.read(8096)
        while chunk:
            yield chunk
            chunk = fp.read(8096)
        else:
            fp.seek(0)

    m = hashlib.md5()
    if isinstance(filename, str):
        with open(filename, 'rb') as f:
            for c in read_chunks(f):
                m.update(c)
    else:
        return ""
    return m.hexdigest()


def copy(src: str) -> None:
    last = src.split('\\')[-1]

    if last not in ignore:
        # copy
        if os.path.isdir(src):
            for s in os.listdir(src):
                copy(os.path.join(src, s))
        else:
            parse = src.replace(':', '') if platform.system() == 'Windows' else src
            dst = os.path.join(dst_dir, parse)

            # mkdir
            folder = os.path.dirname(dst)
            if not os.path.exists(folder):
                os.makedirs(folder)

            # copy
            if not os.path.exists(dst):
                print(src)
                shutil.copyfile(src, dst)
            else:
                # check md5
                src_md5 = md5sum(src)
                dst_md5 = md5sum(dst)
                if src_md5 != dst_md5:
                    print(src)
                    # backup old file
                    m_time = os.stat(dst).st_mtime
                    m_time = time.strftime('_%y%m%d', time.localtime(m_time))
                    base, ext = os.path.splitext(dst)
                    if os.path.exists(base + m_time + ext):
                        os.rename(dst, base + m_time + ext)
                    shutil.copyfile(src, dst)


while True:
    # load config
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
        src_dirs = config['source']
        dst_dir = config['destination']
        ignore = config['ignore']
        backup_time = time.strptime(config['backup_time'], '%H:%M')

    # check time
    now = time.localtime(time.time())
    if now.tm_min == 0:
        print("Check Backup at: " + time.strftime("%Y-%m-%d %H:%M", now))
    if now.tm_hour == backup_time.tm_hour and now.tm_min == backup_time.tm_min:
        for src_dir in src_dirs:
            copy(src_dir)
        now = time.localtime(time.time())
        print("Backup Finished at: " + time.strftime('%Y-%m-%d %H:%M', now))
    time.sleep(60)

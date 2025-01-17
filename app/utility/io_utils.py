import os
from pathlib import Path

from fastapi import UploadFile

from app.utility import constants
from app.models import File

sla_files_path = os.getenv("USER_DIRECTORY_PATH")

def savefiletodisk(file: UploadFile, directory_id, directory_name):
    if file is not None:
        directory_path = sla_files_path + '/' + str(directory_id) + '_' + directory_name + '/files'
        save_path = Path(directory_path, file.filename)
        print(save_path.absolute())

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        with open(save_path, mode='wb') as w:
            w.write(file.file.read())

        if save_path.exists():
            return save_path


def deletefile(file_path):
    if Path(file_path).exists():
        os.remove(file_path)
        return True
    return False

def create_directory_in_disk(directory_name, directory_id):
    directory_path = sla_files_path + '/' + str(directory_id) + '_' + directory_name
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        return directory_path
    else:
        return constants.DIRECTORY_ALREADY_PRESENT_ERR






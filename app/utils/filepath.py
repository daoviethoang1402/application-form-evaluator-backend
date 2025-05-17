import os

STORAGE_DIR = 'app/storage'

def get_file_path(subpath: str, filename: str):
    file_path = os.path.join(STORAGE_DIR, subpath, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{filename}' not found inside '{subpath}'")
    return file_path

def set_file_path(subpath: str, filename: str):
    folder = os.path.join(STORAGE_DIR, subpath)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)
    return file_path

def build_folder_tree():
    result = []
    for root, dirs, files in os.walk(STORAGE_DIR):
        for name in files:
            result.append(os.path.relpath(os.path.join(root, name), STORAGE_DIR))
        for name in dirs:
            result.append(os.path.relpath(os.path.join(root, name), STORAGE_DIR))
    return result
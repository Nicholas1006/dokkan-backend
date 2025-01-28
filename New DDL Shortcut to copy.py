import os
import shutil

def replace_symlinks_with_actual_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            symlink_path = os.path.join(root, file)
            if os.path.islink(symlink_path):
                try:
                    target_path = os.readlink(symlink_path)
                    target_path = os.path.abspath(target_path)
                    if os.path.exists(target_path):
                        os.unlink(symlink_path)
                        shutil.copy2(target_path, symlink_path)
                        print(f"Replaced symlink {symlink_path} with the actual file.")
                    else:
                        print(f"Target file does not exist for symlink: {symlink_path}")
                except Exception as e:
                    print(f"Failed to process symlink {symlink_path}: {e}")

if __name__ == "__main__":
    new_assets_folder = "Dokkan Asset Downloader/NewAssets"
    if os.path.exists(new_assets_folder):
        replace_symlinks_with_actual_files(new_assets_folder)
    else:
        print(f"Directory does not exist: {new_assets_folder}")

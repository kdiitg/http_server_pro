import os
import shutil
import subprocess
import glob
import pathlib
import re

def bump_version(level='patch'):
    version_file = pathlib.Path("http_server_pro") / "__version__.py"
    version_text = version_file.read_text()
    match = re.search(r'__version__ = ["\'](\d+)\.(\d+)\.(\d+)["\']', version_text)

    if not match:
        print("❌ Couldn't find version in __version__.py")
        return

    major, minor, patch = map(int, match.groups())

    if level == 'major':
        major += 1
        minor = 0
        patch = 0
    elif level == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1

    new_version = f"{major}.{minor}.{patch}"
    version_file.write_text(f'__version__ = "{new_version}"\n')
    print(f"🔼 Version bumped to {new_version}")

def clean_build():
    print("🧹 Cleaning previous builds...")
    for folder in ['dist', 'build']:
        shutil.rmtree(folder, ignore_errors=True)
    for egg in glob.glob("*.egg-info"):
        shutil.rmtree(egg, ignore_errors=True)
    print("✅ Clean complete.\n")

def build_package():
    print("📦 Building package...")
    result = subprocess.run(["python", "setup.py", "sdist", "bdist_wheel"])
    if result.returncode == 0:
        print("✅ Build successful.\n")
    else:
        print("❌ Build failed!")
        exit(1)

def upload_package():
    print("🚀 Uploading to PyPI...")
    result = subprocess.run(["twine", "upload", "dist/*"])
    if result.returncode == 0:
        print("✅ Upload successful.")
    else:
        print("❌ Upload failed.")
        exit(1)

def main():
    print("\n📡 PyPI Publisher Script\n------------------------")
    print("1. Build and upload to PyPI")
    print("2. Clean, rebuild, and upload")
    print("3. Auto-bump version, rebuild, upload")
    print("4. Exit")

    choice = input("Choose an option (1/2/3/4): ").strip()

    if choice == "1":
        build_package()
        upload_package()
    elif choice == "2":
        clean_build()
        build_package()
        upload_package()
    elif choice == "3":
        print("🔢 Bump which version level?")
        print("   1. Patch (default)")
        print("   2. Minor")
        print("   3. Major")
        sub = input("   Choose 1/2/3: ").strip()
        level = "patch"
        if sub == "2":
            level = "minor"
        elif sub == "3":
            level = "major"
        bump_version(level)
        clean_build()
        build_package()
        upload_package()
    else:
        print("Exiting...")

if __name__ == "__main__":
    main()




# Import Python's Default Libs
import os
import sys
import subprocess
import stat
import shutil
import pickle
import webbrowser
import time
from pathlib import Path
from datetime import datetime
import platform
import fnmatch

# Clear Console
def clear():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
    # for mac and linux
    else:
        _ = os.system('clear')

# Ensure Errors are readable and Reportable
def show_exception_and_exit(exc_type, exc_value, tb):
    clear()
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    print()
    print("Please report this error to the Github!")
    input("Press Enter to Close Program")
    sys.exit(-1)
sys.excepthook = show_exception_and_exit

# Define Constants
NAME_SM64COOPDX = "SM64CoopDX"
NAME_MANAGER = NAME_SM64COOPDX + " Manager"
NAME_MAIN_MENU = "Main Options"
NAME_MODS_MENU = "Mod Options"
NAME_MANAGER_OPTIONS = "Manager Options"
NAME_FOLDER_OPTIONS = "Mod Folder Toggles"
VERSION = "1"
DATE = datetime.now().strftime("%m/%d/%Y")
PLATFORM_WINDOWS = "Windows"
PLATFORM_LINUX = "Linux"

clear()
print("Booting " + NAME_MANAGER + "...")

# Define Constant Paths
USER_DIR = str(Path.home()).replace("\\", "/")
os.chdir(USER_DIR)
SAVE_DIR = "sm64coopdx-manager.pickle"
def get_appdata_dir():
    systemName = platform.system()
    generalAppdata = ""

    # Get Platform's Appdata Folder
    if systemName == PLATFORM_WINDOWS:
        generalAppdata = USER_DIR + "/AppData/Roaming/"
    elif systemName == PLATFORM_LINUX:
        generalAppdata = USER_DIR + "/.local/share/"
    else:
        clear()
        print(NAME_MANAGER + " is not supported on your Operating System")
        input("Press Enter to Close Program")
        exit()

    # Get Appdata folder for Coop
    if os.path.isdir(generalAppdata + "sm64ex-coop"):
        return generalAppdata + "sm64ex-coop"
    else:
        return generalAppdata + "sm64coopdx"

APPDATA_DIR = get_appdata_dir()
MANAGED_MODS_DIR = APPDATA_DIR + "/managed-mods"
if not os.path.isdir(MANAGED_MODS_DIR):
   os.makedirs(MANAGED_MODS_DIR)

# Install External Libs
import importlib.util
installedModuleList = []
queueRestart = False
def check_module(package):
    packageSpec = importlib.util.find_spec(package)
    if packageSpec == None:
        print("Installing Dependancy '" + package + "'")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    else:
        installedModuleList.append(package)
        return queueRestart

queueRestart = check_module('requests')
queueRestart = check_module('chime')

if queueRestart:
    clear()
    print(NAME_MANAGER + " requires a Restart in order to use Installed Python Libraries")
    input("Press Enter to Restart Program")
    os.execv(sys.executable, ['python'] + sys.argv)
    
import requests
import chime

def github_version_check():
    try:
        return requests.get("https://api.github.com/repos/Squishy6094/sm64coopdx-manager/releases/latest").json()["tag_name"]
    except:
        return None

def clear_with_header():
    clear()

    updateString = github_version_check()
        
    header = NAME_MANAGER + " v" + VERSION + " - " + DATE
    headerBreak = ""
    while len(headerBreak) < len(header):
        headerBreak = headerBreak + "-"
    print(headerBreak)
    print(header)
    if updateString != None and updateString != "v" + VERSION:
        print("Update Avalible! v" + VERSION + " -> " + updateString)
    print(headerBreak)
    print()

SUB_HEADER_LENGTH = 25
def sub_header(headerText):
    subheaderText = " " + headerText + " "
    while len(subheaderText) < SUB_HEADER_LENGTH:
        subheaderText = "-" + subheaderText + "-"
    if len(subheaderText) == SUB_HEADER_LENGTH:
        subheaderText = subheaderText + "-"
    print(subheaderText)



def read_or_new_pickle(path, default):
    if os.path.isfile(path):
        with open(path, "rb") as f:
            try:
                return pickle.load(f)
            except Exception:
                pass
    else:
        with open(path, 'wb') as f:
            pickle.dump(default, f)
    return default

# Save Data
saveData = {
    "coopDir": (USER_DIR + '/Downloads/sm64coopdx/sm64coopdx.exe'),
    "autoBackup": True,
    "loadChime": True,
    "mods-backup": False,
}
saveDataPickle = read_or_new_pickle(SAVE_DIR, saveData)
for s in saveDataPickle:
    saveData[s] = saveDataPickle[s]

def save_field(field, value):
    saveData[field] = value
    with open(SAVE_DIR, "wb") as f:
        pickle.dump(saveData, f)
    return value

def notify():
    if saveData["loadChime"]:
        chime.theme('mario')
        chime.success(sync=True)

def del_rw(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)

def unhide_tree(inputDir):
    for root, dirs, files in os.walk(inputDir):  
        for dir in dirs:
            os.chmod(os.path.join(root, dir), stat.S_IRWXU)
        for file in files:
            os.chmod(os.path.join(root, file), stat.S_IRWXU)    

def folder_from_file_dir(filename):
    filename = filename.replace("\\", "/")
    splitDir = filename.split("/")
    dirCount = 0
    returnString = ""
    for x in splitDir:
        dirCount = dirCount + 1
        if dirCount < len(splitDir):
            returnString = returnString + x + "/"
    return returnString

def backup_mods(wipeModFolder=False, forceBackup=False):
    dir = APPDATA_DIR + "/mods"
    if not saveData["autoBackup"]:
        if not forceBackup:
            print("Skipping Auto-Backup...")
            if wipeModFolder:
                print("Cleaning " + NAME_SM64COOPDX + "'s Appdata Mods Folder...")
                shutil.rmtree(dir, ignore_errors=True, onerror=del_rw)
            return
        else:
            print("Forcing Auto-Backup...")
    if os.path.isdir(dir):
        print("Appdata Mods Folder Found!")
        print("Ensuring " + NAME_SM64COOPDX + "'s Appdata Mods are moveable...")
        unhide_tree(dir)
        #print("Cleaning old Backups...")
        #shutil.rmtree(MANAGED_MODS_DIR + "/backup", ignore_errors=True)
        print("Backing up " + NAME_SM64COOPDX + "'s Appdata Mods Folder...")
        shutil.copytree(dir, MANAGED_MODS_DIR + "/backup", dirs_exist_ok=True)
        if wipeModFolder:
            print("Cleaning " + NAME_SM64COOPDX + "'s Appdata Mods Folder...")
            shutil.rmtree(dir, ignore_errors=True, onerror=del_rw)
    dir = folder_from_file_dir(saveData["coopDir"]) + "/mods"
    if os.path.isdir(dir):
        print("Install Directory Mods Folder Found!")
        print("Ensuring " + NAME_SM64COOPDX + "'s Install Mods are moveable...")
        unhide_tree(dir)
        print("Cleaning " + NAME_MANAGER + "'s Default Folder...")
        shutil.rmtree(MANAGED_MODS_DIR + "/default", ignore_errors=True)
        print("Backing up " + NAME_SM64COOPDX + "'s Install Mods Folder...")
        shutil.copytree(dir, MANAGED_MODS_DIR + "/backup", dirs_exist_ok=True)
        print("Moving " + NAME_SM64COOPDX + "'s Install Mods Folder to Defaults...")
        shutil.move(dir, MANAGED_MODS_DIR + "/default")

clear_with_header()
backup_mods(False)

def include_patterns(*patterns):
    def _ignore_patterns(path, names):
        keep = set(name for pattern in patterns
                            for name in fnmatch.filter(names, pattern))
        ignore = set(name for name in names
                        if name not in keep and not os.path.isdir(os.path.join(path, name)))
        return ignore
    return _ignore_patterns

def get_mod_folders():
    modFolders = []
    for (dirpath, dirnames, filenames) in os.walk(MANAGED_MODS_DIR):
        modFolders.extend(dirnames)
        return modFolders

def load_mod_folders():
    if not os.path.isdir(APPDATA_DIR):
        return
    print("Loading mods...")
    print("Ensuring " + NAME_MANAGER + "'s Mods are moveable...")
    # unhide_tree(APPDATA_DIR + "/mods")
    unhide_tree(MANAGED_MODS_DIR)
    backup_mods(True)
    mods = get_mod_folders()
    for s in saveData:
        for f in mods:
            if s == ("mods-" + f) and saveData[s] == True:
                print("Cloning " + f + " to " + NAME_SM64COOPDX + "'s Mods Folder")
                shutil.copytree(MANAGED_MODS_DIR + "/" + f, APPDATA_DIR + "/mods",
                    ignore=include_patterns('*.lua', '*.luac',
                                            '*.bin', '*.col', '*.c', '*.h',
                                            '*.bhv',
                                            '*.mp3', '*.ogg', '*.m64', '*.aiff',
                                            '*.lvl',
                                            '*.png', '*.tex'), dirs_exist_ok=True)
                break
    notify()

def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        subprocess.call(filename, cwd=folder_from_file_dir(filename))

        
def open_folder(foldername):
    if sys.platform == "win32":
        os.startfile(foldername)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, foldername],)

def boot_coop():
    coopDirectory = saveData["coopDir"]
    print("Standard Boot:")
    load_mod_folders()
    print("Booting " + NAME_SM64COOPDX + " from Directory: '" + coopDirectory + "'")
    open_file(coopDirectory)


def config_coop_dir():
    print("Please enter a new Directory to use for " + NAME_SM64COOPDX)
    print("(Type 'back' to return to " + NAME_MAIN_MENU + ")")
    while(True):
        inputDir = input("> ")
        if os.path.isfile(inputDir):
            return inputDir
        elif inputDir == "back":
            break
        else:
            print("Directory not found, please enter a valid directory")

# Main Options
notify()
while(True):
    clear_with_header()
    sub_header(NAME_MAIN_MENU)
    print("1. Open " + NAME_SM64COOPDX)
    print("2. Mod Options")
    print("3. Manager Options")
    print("4. Support Links")
    print("5. Close Program")

    prompt1 = input("> ")
    if prompt1 == "1": # Open Coop
        while(True):
            clear_with_header()
            if os.path.isfile(saveData["coopDir"]):
                boot_coop()
                break
            else:
                print(NAME_SM64COOPDX + " not found at Directory '" + saveData["coopDir"] + "'")
                config = config_coop_dir()
                if config != None:
                    saveData["coopDir"] = save_field("coopDir", config)
                    clear_with_header()
                    boot_coop()
                    break
                else:
                    break
    if prompt1 == "2": # Mod Options
        while(True):
            clear_with_header()
            if not os.path.isdir(APPDATA_DIR):
                print("Appdata Directory does not exist, please open " + NAME_SM64COOPDX + " first!")
                input("Press Enter to return to " + NAME_MAIN_MENU)
                clear()
            else:
                sub_header(NAME_MODS_MENU)
                print("1. Configure Loaded Mod Folders")
                print("2. Backup and Clear Mods Folder")
                print("3. Open Managed Mods Folder")
                print("4. Back")

            prompt2 = input("> ")
            if prompt2 == "1": # Mod Folder Config
                while(True):
                    clear_with_header()
                    #oldstr.replace("M", "")
                    mods = get_mod_folders()
                    modNum = 0
                    if len(mods) < 1:
                        print(NAME_MANAGER + "'s Managed Mods Folder is empty!")
                        print("Your Managed Mods can be found at: '" + MANAGED_MODS_DIR + "'")
                        input("Press Enter to return to " + NAME_MODS_MENU)
                        break
                    sub_header(NAME_FOLDER_OPTIONS)
                    for x in mods:
                        modOnOff = False
                        modNum = modNum + 1
                        try:
                            modOnOff = saveData["mods-" + x]
                        except:
                            saveData["mods-" + x] = save_field("mods-" + x, True)
                            modOnOff = True
                        spacing = " "
                        while len(spacing) < 25 - (len(x) + 2):
                            spacing = spacing + "."
                        spacing = spacing + " "
                        print(str(modNum) + ". " + x + spacing + ("(O) Enabled" if modOnOff else "(X) Disabled"))
                    print()
                    print("Type a Folder's Name / Number to Toggle it")
                    print("Type 'all' to Enable all Folders")
                    print("Type 'none' to Disable all Folders")
                    print("Type 'apply' to Apply Current Folders without leaving")
                    print("Type 'back' to return to " + NAME_MODS_MENU)
                    prompt3 = input("> ")
                    if prompt3 == "all":
                        for x in mods:
                            save_field("mods-" + x, True)
                    if prompt3 == "none":
                        for x in mods:
                            save_field("mods-" + x, False)
                    if prompt3 == "apply" or prompt3 == "":
                        clear_with_header()
                        load_mod_folders()
                    if prompt3 == "back":
                        clear_with_header()
                        load_mod_folders()
                        break
                    modNum = 0
                    for x in mods:
                        modNum = modNum + 1
                        modNumString = str(modNum)
                        if prompt3 == modNumString or prompt3.lower() == x.lower():
                            modOnOff = False
                            try:
                                modOnOff = saveData["mods-" + x]
                            except:
                                modOnOff = True
                            save_field("mods-" + x, (not modOnOff))
            if prompt2 == "2": # Backup and Clear Mods
                backup_mods(True, True)
                break
            if prompt2 == "3": # Open Appdata
                open_folder(MANAGED_MODS_DIR)
            if prompt2 == "4": # Back
                break
    if prompt1 == "3": # Manager Options
        while(True):
            clear_with_header()
            sub_header(NAME_MANAGER_OPTIONS)
            print("1. Configure Directory")
            print("2. Toggle Auto-Backup (" + str(saveData["autoBackup"]) + ")")
            print("3. Toggle Load Chime (" + str(saveData["loadChime"]) + ")")
            print("4. " + NAME_MANAGER + " Info")
            print("5. Back")

            prompt2 = input("> ")
            if prompt2 == "1": # Set Coop Directory
                clear_with_header()
                while(True):
                    config = config_coop_dir()
                    if config != None:
                        saveData["coopDir"] = save_field("coopDir", config)
                        break
                    else:
                        break
            if prompt2 == "2": # Set Coop Directory
                saveData["autoBackup"] = save_field("autoBackup", not saveData["autoBackup"])
            if prompt2 == "3": # Set Coop Directory
                saveData["loadChime"] = save_field("loadChime", not saveData["loadChime"])
            if prompt2 == "4": # Manager Info
                clear_with_header()
                sub_header("Manager Info")
                print(NAME_MANAGER + " by Squishy6094")
                print("Version " + VERSION + " / Github Version " + str(github_version_check()).replace("v", ""))
                print()
                sub_header("User Info")
                # Executible Exists
                if os.path.isfile(saveData["coopDir"]):
                    print("Executible Directory: '" + saveData["coopDir"] + "'")
                else:
                    print("Executible Directory Invalid")
                # Appdata Exists
                if os.path.isdir(APPDATA_DIR):
                    print("Appdata Directory: '" + APPDATA_DIR + "'")
                else:
                    print("Appdata Directory Invalid")
                # Other Save Data
                print("Auto-Backup Mods: " + str(saveData["autoBackup"]))
                print("Load Chime: " + str(saveData["loadChime"]))
                print()
                sub_header("Library Info")
                print("Required Python Libraries Installed:")
                for x in installedModuleList:
                    print("- " + x)
                print()
                input("Press Enter to return to " + NAME_MAIN_MENU)
            if prompt2 == "5": # Exit
                break
    if prompt1 == "4": # Support Links
        while(True):
            clear_with_header()
            print("Support Links:")
            print("1. Squishy Community - Manager Support - (Discord)")
            print("2. " + NAME_MANAGER + " - Issue Reporting - (Github)")
            print("3. Coop Central - " + NAME_SM64COOPDX + " Support - (Discord)")
            print("4. Back")

            prompt2 = input("> ")
            if prompt2 == "1":
                webbrowser.open("https://discord.gg/HtpXAxrgAw", new=0, autoraise=True)
            if prompt2 == "2":
                webbrowser.open("https://github.com/Squishy6094/sm64coopdx-manager", new=0, autoraise=True)
            if prompt2 == "3":
                webbrowser.open("https://discord.gg/G2zMwjbxdh", new=0, autoraise=True)
            if prompt2 == "4" or prompt2 == "":
                break
    if prompt1 == "5": # Exit
        break
clear()
exit()

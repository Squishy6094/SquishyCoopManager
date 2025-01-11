# Import OS Functions
import os, glob
import stat
import shutil
import pickle
from pathlib import Path
from datetime import datetime
from os import system, name
from subprocess import call

# Define Constants
NAME_SM64COOPDX = "SM64CoopDX"
NAME_MANAGER = "Squishy " + NAME_SM64COOPDX + " Manager"
NAME_MAIN_MENU = "Main Options"
NAME_MODS_MENU = "Mod Options"
VERSION = "1 (In-Dev)"
DATE = datetime.now().strftime("%m/%d/%Y")

USER_DIR = str(Path.home())
SAVE_DIR = "SquishyCoopManager.sav"
APPDATA_DIR = (USER_DIR + "\\AppData\\Roaming\\sm64ex-coop") if os.path.isdir(USER_DIR + "\\AppData\\Roaming\\sm64ex-coop") else (USER_DIR + "\\AppData\\Roaming\\sm64coopdx")
MANAGED_MODS_DIR = APPDATA_DIR + "\\managed-mods"
if not os.path.isdir(MANAGED_MODS_DIR):
   os.makedirs(MANAGED_MODS_DIR)

def read_or_new_pickle(path, default):
    if os.path.isfile(path):
        with open(path, "rb") as f:
            try:
                return pickle.load(f)
            except Exception:
                pass 
    with open(path, "wb") as f:
        pickle.dump(default, f)
    return default

# Save Data
saveData = {
    "coopDir": (USER_DIR + '\\Downloads\\sm64coopdx\\sm64coopdx.exe'),
    "autoBackup": True,
}
saveDataPickle = read_or_new_pickle(SAVE_DIR, saveData)
for s in saveDataPickle:
    saveData[s] = saveDataPickle[s]

def save_field(field, value):
    saveData[field] = value
    with open(SAVE_DIR, "wb") as f:
        pickle.dump(saveData, f)
    return value
   
def clear(header):
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')
        
    if header: # Header
        header = NAME_MANAGER + " v" + VERSION + " - " + DATE
        headerBreak = ""
        while len(headerBreak) < len(header):
            headerBreak = headerBreak + "-"
        print(headerBreak)
        print(header)
        print(headerBreak)
        print()

def del_rw(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)

def unhide_tree(inputDir):
    for root, dirs, files in os.walk(inputDir):  
        for dir in dirs:
            os.chmod(os.path.join(root, dir), stat.S_IRWXU)
        for file in files:
            os.chmod(os.path.join(root, file), stat.S_IRWXU)    

def backup_mods(wipeModFolder):
    if (not os.path.isdir(APPDATA_DIR)) or (not saveData["autoBackup"] and not wipeModFolder):
        return
    clear(True)
    print("Ensuring files are moveable...")
    unhide_tree(APPDATA_DIR + "\\mods")
    unhide_tree(MANAGED_MODS_DIR)
    if os.path.isdir(APPDATA_DIR + "\\mods"):
        print("Cleaning old Backups...")
        shutil.rmtree(MANAGED_MODS_DIR + "\\backup", ignore_errors=True)
        print("Backing up Default Mods Folder...")
        shutil.copytree(APPDATA_DIR + "\\mods", MANAGED_MODS_DIR + "\\backup", ignore=shutil.ignore_patterns('*.pyc', 'tmp*'))
        if wipeModFolder:
            print("Clearing Default Mods Folder...")
            shutil.rmtree(APPDATA_DIR + "\\mods", ignore_errors=True, onerror=del_rw)

backup_mods(False)

def load_mod_folders():
    if not os.path.isdir(APPDATA_DIR):
        return
    clear(True)
    print("Ensuring files are moveable...")
    unhide_tree(APPDATA_DIR + "\\mods")
    unhide_tree(MANAGED_MODS_DIR)
    backup_mods(True)
    for s in saveData:
        for f in modFolders:
            if s == ("mods-" + f) and saveData[s] == True:
                print("Cloning " + f + " to Default Mods Folder")
                shutil.copytree(MANAGED_MODS_DIR + "\\" + f, APPDATA_DIR + "\\mods", ignore=shutil.ignore_patterns('*.pyc', 'tmp*'), dirs_exist_ok=True)
                break

def config_coop_dir():
    print("Please enter a new Directory to use for " + NAME_SM64COOPDX)
    print("(Type 'back' to return to " + NAME_MAIN_MENU + ")")
    while(True):
        inputDir = input()
        if os.path.isfile(inputDir):
            return inputDir
        elif inputDir == "back":
            break
        else:
            print("Directory not found, please enter a valid directory")

# Main Options
while(True):
    clear(True)
    print(NAME_MAIN_MENU + ":")
    print("1. Open " + NAME_SM64COOPDX)
    print("2. Mod Options")
    print("3. Manager Options")
    print("4. Close Program")

    prompt1 = input()
    if prompt1 == "1": # Open Coop
        while(True):
            clear(True)
            if os.path.isfile(saveData["coopDir"]):
                print("Opening from Directory: '" + saveData["coopDir"] + "'")
                load_mod_folders()
                os.startfile(saveData["coopDir"])
                break
            else:
                print(NAME_SM64COOPDX + " not found at Directory '" + saveData["coopDir"] + "'")
                config = config_coop_dir()
                if config != None:
                    saveData["coopDir"] = save_field("coopDir", config)
                    load_mod_folders()
                    os.startfile(saveData["coopDir"])
                    break
                else:
                    break
    if prompt1 == "2": # Mod Options
        while(True):
            clear(True)
            if not os.path.isdir(APPDATA_DIR):
                print("Appdata Directory does not exist, please open " + NAME_SM64COOPDX + " first!")
                input("Press Enter to return to Main Options")
                clear(False)
            else:
                print(NAME_MODS_MENU + ":")
                print("1. Configure Loaded Mod Folders")
                print("2. Backup and Clear Mods Folder")
                print("3. Open Appdata")
                print("4. Back")

            prompt2 = input()
            if prompt2 == "1": # Mod Folder Config
                while(True):
                    clear(True)
                    print("Mod Folders:")
                    #oldstr.replace("M", "")
                    modFolders = []
                    modNum = 0
                    for (dirpath, dirnames, filenames) in os.walk(MANAGED_MODS_DIR):
                        modFolders.extend(dirnames)
                        break
                    for x in modFolders:
                        modOnOff = False
                        modNum = modNum + 1
                        try:
                            modOnOff = saveData["mods-" + x]
                        except:
                            saveData["mods-" + x] = save_field("mods-" + x, True)
                            modOnOff = True
                        print(str(modNum) + ". " + x + " - " + ("Enabled" if modOnOff else "Disabled"))
                    print()
                    print("Type a Folder's Name or it's Number to Toggle it")
                    print("Type 'all' to Enable all Folders")
                    print("Type 'none' to Disable all Folders")
                    print("Type 'back' to return to " + NAME_MODS_MENU)
                    prompt3 = input()
                    if prompt3 == "all":
                        for x in modFolders:
                            save_field("mods-" + x, True)
                    if prompt3 == "none":
                        for x in modFolders:
                            save_field("mods-" + x, False)
                    if prompt3 == "back":
                        load_mod_folders()
                        break
                    modNum = 0
                    for x in modFolders:
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
                backup_mods(True)
                break
            if prompt2 == "3": # Open Appdata
                os.startfile(APPDATA_DIR)
            if prompt2 == "4": # Back
                break
    if prompt1 == "3": # Manager Options
        while(True):
            clear(True)
            print("Manager Options:")
            print("1. Configure Directory")
            print("2. Toggle Auto-Backup (" + str(saveData["autoBackup"]) + ")")
            print("3. " + NAME_MANAGER + " Info")
            print("4. Back")

            prompt2 = input()
            if prompt2 == "1": # Set Coop Directory
                clear(True)
                while(True):
                    config = config_coop_dir()
                    if config != None:
                        saveData["coopDir"] = save_field("coopDir", config)
                        os.startfile(saveData["coopDir"])
                        break
                    else:
                        break
            if prompt2 == "2": # Set Coop Directory
                saveData["autoBackup"] = save_field("autoBackup", not saveData["autoBackup"])
            if prompt2 == "3": # Squishy Manager Info
                clear(True)
                print(NAME_MANAGER)
                print("Version " + VERSION)
                print()
                print("Executible Directory: '" + saveData["coopDir"] + "'")
                print(" Executible Exists: " + str(os.path.isfile(saveData["coopDir"])))
                print("Appdata Directory: '" + APPDATA_DIR + "'")
                print(" Directory Exists: " + str(os.path.isdir(APPDATA_DIR)))
                print("")
                input("Press Enter to return to " + NAME_MAIN_MENU)
            if prompt2 == "4": # Exit
                break
    if prompt1 == "4": # Exit
        break
clear(False)
exit()

from .default_files import defaults

def getCurrentlySelectedFile():
    TEMP_FILE = "__currently_selected__.txt"
    os.system(f"\"{defaults.AHK}\" {defaults.WINDOWS_SCRIPTS_FOLDER}/{defaults.GET_FILE_AHK_SCRIPT_FILE} {TEMP_FILE}")

    f = open(TEMP_FILE)
    result = f.read()
    f.close()

    os.remove(TEMP_FILE)
    return result

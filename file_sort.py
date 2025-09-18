import os
import shutil
from collections import defaultdict
import time
import sys

# -- Platform-specific setup --
if os.name == 'nt':
    os.system('') # Enables ANSI escape codes in Windows command prompt

# -- ASCII Art Design --

class COLORS:
    """ANSI color codes (Monochrome version). Text attributes like BOLD are kept."""
    # All color codes are empty strings to disable color
    B1 = B2 = B3 = B4 = B5 = B6 = ''
    HIGHLIGHT = ''
    SHADOW_L1 = SHADOW_L2 = ''
    WHITE = GREEN = YELLOW = RED = ''
    # Keep ENDC to reset attributes
    ENDC = '\033[0m'
    # Keep Bold and Underline for emphasis without color
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Prints a stylish monochrome banner for 'FILE SORT'."""
    banner_lines = [
        " ________ ___  ___       _______           ________  ________  ________  _________   ",
        "│╲  _____╲╲  ╲│╲  ╲     │╲  ___ ╲         │╲   ____╲│╲   __  ╲│╲   __  ╲│╲___   ___╲ ",
        "╲ ╲  ╲__╱╲ ╲  ╲ ╲  ╲    ╲ ╲   __╱│        ╲ ╲  ╲___│╲ ╲  ╲│╲  ╲ ╲  ╲│╲  ╲│___ ╲  ╲_│ ",
        " ╲ ╲   __╲╲ ╲  ╲ ╲  ╲    ╲ ╲  ╲_│╱__       ╲ ╲_____  ╲ ╲  ╲╲╲  ╲ ╲   _  _╲   ╲ ╲  ╲  ",
        "  ╲ ╲  ╲_│ ╲ ╲  ╲ ╲  ╲____╲ ╲  ╲_│╲ ╲       ╲│____│╲  ╲ ╲  ╲╲╲  ╲ ╲  ╲╲  ╲│   ╲ ╲  ╲ ",
        "   ╲ ╲__╲   ╲ ╲__╲ ╲_______╲ ╲_______╲        ____╲_╲  ╲ ╲_______╲ ╲__╲╲ _╲    ╲ ╲__╲",
        "    ╲│__│    ╲│__│╲│_______│╲│_______│       │╲_________╲│_______│╲│__│╲│__│    ╲│__│",
        "                                             ╲│_________│                            ",
        "                                                                                     "
    ]
    for line in banner_lines:
        print(f"{COLORS.BOLD}{line}{COLORS.ENDC}")

# -- Language Translations --
TRANSLATIONS = {
    "en": {
        # "welcome_desc": "This script will help you sort files from a folder into categorized directories.",
        "choose_folder_prompt": "Please choose a folder to organize",
        "folder_list_header": "Default directories found:",
        "home_dir_header": "Default directories not found. Here is your home directory:",
        "no_folders_found": "No directories were found to choose from.",
        "please_enter_path_manually": "Please enter the full path to the folder you want to organize.",
        "enter_path_manually": "Enter path manually",
        "your_choice": "Your choice: ",
        "enter_folder_path": "Enter the folder path: ",
        "error_dir_not_found": "[Error] Directory '{path}' not found.",
        "invalid_choice": "[Error] Invalid choice. Please try again.",
        "scanning_directory": "Scanning and planning...",
        "no_files_to_process": "No files found to process in this directory.",
        "created_directory": "--> Created directory: {category_path}",
        "failed_to_move": "[Error] Failed to move '{filename}'. Reason: {e}",
        "stage_log": "Stage {current}/{total}: Moving {count} files to '{category}'",
        "sorting_complete_title": "Sorting Complete!",
        "total_files_processed": "Total files processed: {total_files}",
        "files_moved_by_category": "Files moved by category:",
        "no_files_moved": "No files were moved.",
        "file_categories": {
            "Images": "Images", "Documents": "Documents", "Videos": "Videos", "Music": "Music",
            "Archives": "Archives", "Scripts": "Scripts", "Other": "Other"
        }
    },
    "uk": {
        # "welcome_desc": "Цей скрипт допоможе вам сортувати файли з теки в категоризовані директорії.",
        "choose_folder_prompt": "Будь ласка, оберіть теку для сортування",
        "folder_list_header": "Знайдено стандартні теки:",
        "home_dir_header": "Стандартні теки не знайдено. Ось ваша домашня директорія:",
        "no_folders_found": "Не знайдено тек для вибору.",
        "please_enter_path_manually": "Будь ласка, введіть повний шлях до теки, яку ви хочете відсортувати.",
        "enter_path_manually": "Ввести шлях вручну",
        "your_choice": "Ваш вибір: ",
        "enter_folder_path": "Введіть шлях до теки: ",
        "error_dir_not_found": "[Помилка] Директорію '{path}' не знайдено.",
        "invalid_choice": "[Помилка] Неправильний вибір. Будь ласка, спробуйте ще раз.",
        "scanning_directory": "Сканування та планування...",
        "no_files_to_process": "Не знайдено файлів для обробки в цій директорії.",
        "created_directory": "--> Створено директорію: {category_path}",
        "failed_to_move": "[Помилка] Не вдалося перемістити '{filename}'. Причина: {e}",
        "stage_log": "Етап {current}/{total}: Переміщення {count} файлів до '{category}'",
        "sorting_complete_title": "Сортування завершено!",
        "total_files_processed": "Всього оброблено файлів: {total_files}",
        "files_moved_by_category": "Переміщено файлів за категоріями:",
        "no_files_moved": "Жодного файлу не було переміщено.",
        "file_categories": {
            "Images": "Зображення", "Documents": "Документи", "Videos": "Відео", "Music": "Музика",
            "Archives": "Архіви", "Scripts": "Скрипти", "Other": "Інше"
        }
    }
}

# Global translator function
_ = None

def get_translator(language="en"):
    translations = TRANSLATIONS.get(language, TRANSLATIONS["en"])
    def translator(key, **kwargs):
        text = translations.get(key, key)
        return text.format(**kwargs) if isinstance(text, str) else text
    return translator

# -- Main Logic --

BASE_FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx", ".odt"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    "Music": [".mp3", ".wav", ".ogg", ".flac"],
    "Archives": [".zip", ".rar", ".tar", ".gz", ".7z"],
    "Scripts": [".py", ".js", ".sh", ".bat"],
    "Other": []
}

def get_category(file_extension):
    for category, extensions in BASE_FILE_CATEGORIES.items():
        if file_extension.lower() in extensions: return category
    return "Other"

def organize_directory(path, translator):
    if not os.path.isdir(path):
        print(f"{COLORS.BOLD}{COLORS.UNDERLINE}{translator('error_dir_not_found', path=path)}{COLORS.ENDC}")
        return

    print(f"\n{COLORS.BOLD}{translator('scanning_directory')}{COLORS.ENDC}")
    home_dir = os.path.expanduser("~")
    translated_category_names = translator("file_categories")
    files_by_category = defaultdict(list)
    try:
        all_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    except OSError as e:
        print(f"{COLORS.BOLD}[Error] Error reading directory: {e}{COLORS.ENDC}")
        return

    for filename in all_files:
        file_extension = os.path.splitext(filename)[1]
        english_category = get_category(file_extension)
        files_by_category[english_category].append(filename)

    if not files_by_category:
        print(f"\n{COLORS.BOLD}{COLORS.UNDERLINE}{translator('no_files_to_process')}{COLORS.ENDC}")
        return

    total_categories = len(files_by_category)
    moved_files_count = defaultdict(int)
    total_moved = 0

    for i, (english_category, files) in enumerate(files_by_category.items()):
        translated_name = translated_category_names[english_category] if english_category in translated_category_names else english_category
        stage_log = translator('stage_log', current=i+1, total=total_categories, count=len(files), category=translated_name)
        print(f"\n{COLORS.BOLD}{'-'*60}\n{stage_log}{COLORS.ENDC}")
        category_path = os.path.join(home_dir, english_category)
        if not os.path.exists(category_path):
            os.makedirs(category_path)
            print(f"{COLORS.BOLD}  {translator('created_directory', category_path=category_path)}{COLORS.ENDC}")
        for j, filename in enumerate(files):
            progress = (j + 1) / len(files)
            bar_length = 40
            filled_length = int(bar_length * progress)
            bar = f"{'█' * filled_length}{'-' * (bar_length - filled_length)}"
            print(f'\r  [{bar}] {progress:.0%} - {filename}', end='', flush=True)
            try:
                shutil.move(os.path.join(path, filename), os.path.join(category_path, filename))
                moved_files_count[english_category] += 1
                total_moved += 1
            except Exception as e:
                print(f"\n{COLORS.BOLD}{COLORS.UNDERLINE}{translator('failed_to_move', filename=filename, e=e)}{COLORS.ENDC}")
            time.sleep(0.02)
        print()
    title = f" {translator('sorting_complete_title')} "
    print(f"\n{COLORS.BOLD}{'='*70}\n{title.center(70)}\n{'='*70}{COLORS.ENDC}")
    print(f"\n{COLORS.BOLD}{translator('total_files_processed', total_files=total_moved)}{COLORS.ENDC}")
    if moved_files_count:
        print(f"\n{COLORS.UNDERLINE}{translator('files_moved_by_category')}{COLORS.ENDC}")
        for category, count in sorted(moved_files_count.items()):
            translated_name = translated_category_names[category] if category in translated_category_names else category
            print(f"  - {COLORS.BOLD}{translated_name}{COLORS.ENDC}: {count}")
    else:
        print(f"\n{COLORS.BOLD}{COLORS.UNDERLINE}{translator('no_files_moved')}{COLORS.ENDC}")
    print("\n" + f"{COLORS.BOLD}{'-'*70}{COLORS.ENDC}")

def get_cross_platform_user_dirs():
    """Gets standard user directories in a cross-platform way."""
    home = os.path.expanduser("~")
    standard_dirs = ["Documents", "Downloads", "Desktop", "Pictures", "Music", "Videos"]
    dirs = {}
    for d in standard_dirs:
        path = os.path.join(home, d)
        if os.path.isdir(path):
            dirs[d] = path
    return dirs

def main():
    print(f"{COLORS.BOLD}Choose your language / Оберіть вашу мову:{COLORS.ENDC}")
    print(f"{COLORS.BOLD}1. English{COLORS.ENDC}")
    print(f"{COLORS.BOLD}2. Українська (Ukrainian){COLORS.ENDC}")
    lang_choice = ""
    while lang_choice not in ["1", "2"]: lang_choice = input(f"{COLORS.BOLD}Your choice / Ваш вибір: {COLORS.ENDC}").strip()
    translator = get_translator("uk" if lang_choice == "2" else "en")
    clear_screen()
    print_banner()
    # print(f"{COLORS.UNDERLINE}{translator('welcome_desc')}{COLORS.ENDC}\n")
    dir_options = get_cross_platform_user_dirs()
    if not dir_options:
        home_path = os.path.expanduser("~")
        try:
            dir_options = {d: os.path.join(home_path, d) for d in os.listdir(home_path) if os.path.isdir(os.path.join(home_path, d)) and not d.startswith('.')}
        except OSError:
            dir_options = {}
    sorted_dirs = sorted(dir_options.items(), key=lambda item: item[0].lower())
    target_path = ""
    while not target_path:
        print(f"{COLORS.BOLD}{translator('choose_folder_prompt')}{COLORS.ENDC}")
        print(f"{COLORS.BOLD}{'-' * 40}{COLORS.ENDC}")
        if sorted_dirs:
            for i, (name, path) in enumerate(sorted_dirs):
                print(f"  {COLORS.BOLD}{i + 1}. {name}{COLORS.ENDC}")
                print(f"     ↳ {COLORS.UNDERLINE}{path}{COLORS.ENDC}")
            print(f"\n  {COLORS.BOLD}{len(sorted_dirs) + 1}. {translator('enter_path_manually')}{COLORS.ENDC}")
            print(f"{COLORS.BOLD}{'-' * 40}{COLORS.ENDC}")
            try:
                choice = input(f"\n{COLORS.BOLD}{translator('your_choice')}{COLORS.ENDC}").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(sorted_dirs):
                    target_path = sorted_dirs[choice_num - 1][1]
                elif choice_num == len(sorted_dirs) + 1:
                    manual_path = os.path.expanduser(input(f"{COLORS.UNDERLINE}{translator('enter_folder_path')}{COLORS.ENDC}").strip())
                    if os.path.isdir(manual_path): target_path = manual_path
                    else: print(f"{COLORS.BOLD}{COLORS.UNDERLINE}{translator('error_dir_not_found', path=manual_path)}{COLORS.ENDC}")
                else: print(f"{COLORS.BOLD}{COLORS.UNDERLINE}{translator('invalid_choice')}{COLORS.ENDC}")
            except (ValueError, IndexError):
                print(f"{COLORS.BOLD}{COLORS.UNDERLINE}{translator('invalid_choice')}{COLORS.ENDC}")
        else:
            print(f"\n{COLORS.BOLD}{COLORS.UNDERLINE}{translator('no_folders_found')}{COLORS.ENDC}")
            print(f"{COLORS.UNDERLINE}{translator('please_enter_path_manually')}{COLORS.ENDC}")
            try:
                manual_path = os.path.expanduser(input(f"\n{COLORS.UNDERLINE}{translator('enter_folder_path')}{COLORS.ENDC}").strip())
                if os.path.isdir(manual_path):
                    target_path = manual_path
                else:
                    print(f"{COLORS.BOLD}{COLORS.UNDERLINE}{translator('error_dir_not_found', path=manual_path)}{COLORS.ENDC}")
            except Exception as e:
                print(f"{COLORS.BOLD}[Error] {e}{COLORS.ENDC}")
    organize_directory(target_path, translator)

if __name__ == "__main__":
    try: main() 
    except KeyboardInterrupt: print(f"\n\nOperation cancelled by user."); sys.exit(0)

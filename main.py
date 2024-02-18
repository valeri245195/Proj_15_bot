import re
import sys
import shutil
from pathlib import Path
import pickle as p
from datetime import datetime
from collections import UserDict

UKRAINIAN_SYMBOLS = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = (
    "a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t",
    "u",
    "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")
TRANS = {}
for key, value in zip(UKRAINIAN_SYMBOLS, TRANSLATION):
    TRANS[ord(key)] = value
    TRANS[ord(key.upper())] = value.upper()

images_files = list()
video_files = list()
documents_files = list()
audio_files = list()
archives_files = list()
folders = list()
other = list()
unknown = set()
extensions = set()

image_extensions = ['JPEG', 'PNG', 'JPG', 'SVG']
video_extensions = ['AVI', 'MP4', 'MOV', 'MKV']
audio_extensions = ['MP3', 'OGG', 'WAV', 'AMR']
documents_extensions = ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX']
archives_extensions = ['ZIP', 'GZ', 'TAR']

list_of_all_extensions = (
        image_extensions + video_extensions +
        audio_extensions + documents_extensions +
        archives_extensions
)

registered_extensions = dict()
registered_extensions.update({i: 'images' for i in image_extensions})
registered_extensions.update({i: 'video' for i in video_extensions})
registered_extensions.update({i: 'audio' for i in audio_extensions})
registered_extensions.update({i: 'documents' for i in documents_extensions})
registered_extensions.update({i: 'archives' for i in archives_extensions})


class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    def is_valid(self, value):
        True

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if self.is_valid(value):
            self.__value = value
        else:
            raise ValueError("Invalid value")

    def __str__(self):
        return str(self.__value)


class Name(Field):
    pass


class Address(Field):
    pass


class Birthday(Field):

    def is_valid(self, str_birthday):
        pattern = r'\d{2}\.\d{2}\.\d{4}'
        search = re.findall(pattern, value)
        if value == search[0]:
            day, month, year = value.split(".")
            try:
                new_value = datetime(day=int(day), month=int(month), year=int(year))
                return True
            except ValueError:
                return False
        else:
            return False

    def __repr__(self):
        return f'{self.value.strftime("%d %m %Y")}'


class Phone(Field):

    def is_valid(self, phone):
        pattern = r'\d{10}'
        searcher = re.findall(pattern, str(phone))
        phone = searcher[0]
        if phone == searcher[0]:
            return True
        else:
            return False


class Email(Field):

    def is_valid(self, email):
        True


class Record:
    def __init__(self, name, phone=None, birthday=None, email=None, address=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday)  # if birthday else None
        self.email = Email(email)
        self.address = Address(address)

    def days_to_birthday(self, current_date=None):
        if not current_date:
            current_date = datetime.now().date()

        if self.birthday:
            next_birthday = datetime.strptime(str(self.birthday), '%d.%m.%Y').date().replace(year=current_date.year)

            if current_date > next_birthday:
                next_birthday = next_birthday.replace(year=current_date.year + 1)

            days_remaining = (next_birthday - current_date).days
            return f"Days till the next Birthday for {self.name}: {days_remaining} days"
        else:
            return "Birth date not added"

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError

    def edit_phone(self, old_phone, new_phone):
        for i in self.phones:
            if i.value == old_phone:
                i.value = new_phone
                return f'Number {old_phone} from {self.name}\'s list changed to {new_phone}'
            else:
                raise ValueError(f'phone {old_phone} is not find for name {self.name}')
        return f'Number {old_phone} is not exist in {self.name} list'

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        return f"Name: {self.name.value}, phones: {', '.join(str(p) for p in self.phones)}"


class AddressBook(UserDict):
    def __iter__(self, n):
        self.n = n
        self.count = 0
        return self

    def __next__(self):
        self.count += 1
        if self.count > self.n:
            raise StopIteration
        else:
            for i in self.data:
                yield self.data[i]

    def search_contact(self, query):
        matching_contacts = list()

        # Check if the query matches any phone numbers
        for record in self.data.values():
            for phone in record.phones:
                if query in phone.value:
                    matching_contacts.append(record)
                    break

        # Check if the query matches any names
        for record in self.data.values():
            if query.lower() in record.name.value.lower():
                matching_contacts.append(record)

        return matching_contacts

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def save_data_to_disk(self, filename='address_book.pickle'):
        with open(filename, 'wb') as file:
            p.dump(self.data, file)

    def load_data_from_disk(self, filename='address_book.pickle'):
        try:
            with open(filename, 'rb') as file:
                self.data = p.load(file)
        except FileNotFoundError:
            return f'file {func_delete} not find.'

    def __str__(self) -> str:
        return "\n".join(str(r) for r in self.data.values())


def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except IndexError:
            return "Not enough params"
        except KeyError:
            return f"There is no contact such in phone book."
        except ValueError:
            return "Not enough params or wrong phone format"

    return inner


def add_note():
    title = input("Введіть заголовок нотатки: ")
    content = input("Введіть текст нотатки: ")
    tags = input("Введіть теги (розділіть їх комами): ").split(', ')

    note = {'title': title, 'content': content, 'tags': tags}
    notes.append(note)
    print("Нотатка успішно додана!")


def view_notes():
    if not notes:
        print("Немає доступних нотаток.")
        return

    for i, note in enumerate(notes):
        print(f"\nНотатка {i + 1}:")
        print(f"Заголовок: {note['title']}")
        print(f"Текст: {note['content']}")
        print(f"Теги: {', '.join(note['tags'])}")


def search_by_tag():
    tag_to_search = input("Введіть тег для пошуку: ")
    matching_notes = [note for note in notes if tag_to_search.lower() in map(str.lower, note['tags'])]

    if matching_notes:
        print(f"\nЗнайдені нотатки за тегом '{tag_to_search}':")
        for i, note in enumerate(matching_notes):
            print(f"\nНотатка {i + 1}:")
            print(f"Заголовок: {note['title']}")
            print(f"Текст: {note['content']}")
            print(f"Теги: {', '.join(note['tags'])}")
    else:
        print(f"Нотаток з тегом '{tag_to_search}' не знайдено.")


@input_error
def func_search_contacts(*args):
    query = args[0]
    matching_contacts = address_book.search_contact(query)

    if matching_contacts:
        result = '\n'.join(str(record) for record in matching_contacts)
        return f'Matching contacts: \n{result}'
    else:
        return f'No contacts found for query: {query}'


@input_error
def func_help():
    return ('Hi! If you want to start working, just enter "hello"\n' +
            'Number phone in 10 numbers, for example 0001230001\n' +
            'The representation of all commands looks as follows:\n' +
            '"hello" - start work with bot\n' +
            '"add" name phone\n' +
            '"change" name old_phone new_phone\n' +
            '"phone" name\n' +
            '"show all" - for show all information\n' +
            '"good bye", "close", "exit" - for end work\n' +
            '"delete" - delete info of name\n' +
            '"search" - command for search. Just enter "search" and something about contact like name or phone')


@input_error
def parser(user_input: str):
    COMMANDS = {
        "Hello": func_hello,
        "Add ": func_add,
        "Change ": func_change,
        "Phone ": func_search,
        "Show All": func_show_all,
        "Delete ": func_delete,
        "Search ": func_search_contacts,
        "Sort ": do_sort_folder,
        "Add note ": add_note,
        "View notes ": view_notes,
        "Search tag": search_by_tag
    }

    user_input = user_input.title()

    for kw, command in COMMANDS.items():
        if user_input.startswith(kw):
            return command, user_input[len(kw):].strip().split()
    return func_unknown_command, []


@input_error
def func_add(*args):
    print(*args)
    name = args[0]
    record = Record(name)
    phone_numbers = args[1:]
    for phone_number in phone_numbers:
        record.add_phone(phone_number)
    address_book.add_record(record)
    return "Info saved successfully."


@input_error
def func_change(*args):
    for k, v in address_book.items():
        if k == args[0]:
            rec = address_book[args[0]]
            return rec.edit_phone(args[1], args[2])
    return f'{args[0]} isn`t exist in list of names'


@input_error
def func_delete(*args):
    name = args[0]

    if name in address_book:
        address_book.delete(name)
        return f"User {name} has been deleted from the phone book"
    else:
        return f'User {name} is not in the address book'


@input_error
def func_search(*args):
    name = args[0]
    record = address_book.find(name)
    if record:
        return str(record)
    else:
        raise KeyError


@input_error
def func_show_all(*args):
    return str(address_book)


@input_error
def func_unknown_command():
    return "Unknown command. Try again."


@input_error
def func_hello():
    return "How can I help you?"


@input_error
def func_quit():
    return "Good bye!"


def normalize(name: str) -> str:
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', '_', new_name)
    return f"{new_name}.{'.'.join(extension)}"


def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()


def scan(folder):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in list_of_all_extensions:
                folders.append(item)
                scan(item)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder / item.name
        if not extension:
            other.append(new_name)
        else:
            try:
                container = registered_extensions[extension]
                extensions.add(extension)
                globals()[container + "_files"].append(new_name)
            except KeyError:
                unknown.add(extension)
                other.append(new_name)


def handle_file(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)

    new_name = normalize(path.name)
    new_path = target_folder / new_name

    print(f"Moving {path} to {new_path}")

    if path.exists():
        path.replace(new_path)
    else:
        print(f"Error: File {path} not found.")


def handle_archive(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)
    new_name = normalize(path.name.replace(".zip", '').replace('.tar', '').replace('.gz', ''))
    archive_folder = target_folder / new_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path.resolve()), str(archive_folder.resolve()))
    except shutil.ReadError:
        archive_folder.rmdir()
        path.unlink()
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        path.unlink()
        return
    path.unlink()


def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)

    try:
        path.rmdir()
        print(f"Removed empty folder: {path}")
    except OSError as e:
        print(f"Error removing folder {path}: {e}")


def do_sort_folder(*args):
    folder_path = Path(args[0])
    print(folder_path)
    scan(folder_path)

    print(f'Start in {folder_path}')

    file_types = {
        'images': images_files,
        'documents': documents_files,
        'audio': audio_files,
        'video': video_files,
        'archives': archives_files,
        'other': other
    }

    for file_type, files in file_types.items():
        for file in files:
            if file_type == 'archives':
                handle_archive(file, folder_path, file_type)
            else:
                handle_file(file, folder_path, file_type)

    remove_empty_folders(folder_path)

    # Rest of the code remains unchanged
    print("Contents of Organized Folders:")
    for item in folder_path.iterdir():
        if item.is_dir():
            print(f"Folder: {item}")
            for subitem in item.iterdir():
                print(f"  {subitem}")
        else:
            print(f"File: {item}")
    print(f'images: {[normalize(file.name) for file in images_files]}')
    print(f'video: {[normalize(file.name) for file in video_files]}')
    print(f'documents: {[normalize(file.name) for file in documents_files]}')
    print(f'audio: {[normalize(file.name) for file in audio_files]}')
    print(f'archives: {[normalize(file.name) for file in archives_files]}')
    print(f"other: {[normalize(file.name) for file in other]}")
    print(f"unknowns extensions: {[normalize(ext) for ext in unknown]}")
    print(f"unique extensions: {[normalize(ext) for ext in extensions]}")


address_book = AddressBook()


def main():
    print(func_help())

    # load data from disk if data is available
    address_book.load_data_from_disk()

    while True:
        user_input = input('Please, enter the valid command: ')

        if user_input.lower() in ["exit", "close", "good bye"]:
            address_book.save_data_to_disk()
            print(func_quit())
            break
        else:
            handler, arguments = parser(user_input)
            print(handler(*arguments))


if __name__ == '__main__':
    main()

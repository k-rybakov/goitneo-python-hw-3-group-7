from collections import UserDict
from datetime import datetime, timedelta
from collections import defaultdict
from os.path import exists
import re
import pickle

class FieldValidationException(Exception):
    pass

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not len(value): raise FieldValidationException('Name can not be empty')
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if re.search('^\d{10}$', str(value)) == None:
            raise FieldValidationException("Phone must be 10 digits")
        super().__init__(value)

class BirthDay(Field):
    FORMAT = "%d.%m.%Y"
    def __init__(self, value):
        try:
            date = datetime.strptime(value, BirthDay.FORMAT)
            if date > datetime.now():
                raise FieldValidationException('Birthday can not be in future')
            super().__init__(value)
        except ValueError as e:
            message = str(e)
            if 'does not match format' in str(e):
                message = 'Date format must be DD.MM.YYYY'
            raise FieldValidationException(message)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return 'Phone already exists'
        self.phones.append(Phone(phone))
        return 'Phone added'

    def edit_phone(self, old, new):
        for phone_obj in self.phones:
            if phone_obj.value == old:
                new_phone_obj = Phone(new)
                self.phones.remove(phone_obj)
                self.phones.append(new_phone_obj)
                return True
        return False
        
    def find_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return phone
        return None
    
    def show_phones(self):
        return ', '.join(list(map(lambda x: x.value, self.phones)))

    def add_birthday(self, date):
        self.birthday = BirthDay(date)

    def show_birthday(self):
        return 'Date not added' if self.birthday is None else self.birthday.value
 
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):

    def __init__(self, storage='memory', path='contacts.dat'):
        self.storage = storage
        self.file_path = path
        super().__init__()   
        
    def add_record(self, record):
        if not isinstance(record, Record):
            raise TypeError('Expected argument of type Record')
        if self.data.get(record.name.value):
            return 'Contact already added'
        self.data[record.name.value] = record
        self._update_storage()
        return 'Contact added'
    
    def update_record(self, record):
        if not isinstance(record, Record):
            raise TypeError('Expected argument of type Record')
        self.data[record.name.value] = record
        self._update_storage()

    def delete(self, name):
        if self.data.get(name):
            self.data.pop(name)
            self._update_storage()
            return 'Contact deleted'
        return 'Contact not found'
    
    def find(self, name):
        return self.data.get(name, None)
    
    def get_all(self):
        return self._get_from_storage()
    
    def get_birthdays_per_week(self):
        today = datetime.today().date()
        # first day to collect birthdays is Saturday of the current week
        # "today" is not the best day for start since we can run the script on Sunday of the current week and lose weekend birthdays
        this_week_saturday = today + timedelta(days=(5 - today.weekday()))

        result = defaultdict(list)
        
        for name, record in self._get_from_storage().items():
            if record.birthday == None:
                continue
            birthday = datetime.strptime(record.birthday.value, BirthDay.FORMAT).date()
            birthday_this_year = birthday.replace(year=today.year)

            if birthday_this_year < this_week_saturday:
                birthday_this_year = birthday.replace(year=today.year + 1)

            delta_days = (birthday_this_year - this_week_saturday).days

            if delta_days < 7:
                day_name = birthday_this_year.strftime('%A')
                if day_name in ('Saturday', 'Sunday'):
                    day_name = 'Monday'
                result[day_name].append(name)
                
        for day, names in result.items():
            print(f"{day}: {', '.join(name.capitalize() for name in names)}")

    def _update_storage(self):
        if self.storage == 'file':
            with open(self.file_path, 'wb') as fh:
                pickle.dump(self.data, fh)

    def _get_from_storage(self):
        if self.storage == 'file' and exists(self.file_path):
            with open(self.file_path, 'rb') as fh:
                return pickle.load(fh)
        return self.data


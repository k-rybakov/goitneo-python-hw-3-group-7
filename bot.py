from oop_assistant import Record, AddressBook, FieldValidationException

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "_"
    return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip().lower()
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            try:
                name, phone = args
                record = Record(name)
                record.add_phone(phone)
                book.add_record(record)
                print("Contact added")
            except ValueError:
                print('Enter name and phone')
            except FieldValidationException as e:
                print(str(e))
        elif command == "change":
            try:
                name, old_phone, new_phone = args 
                record = book.find(name)
                if record is None: 
                    print('Contact not found')
                elif record.find_phone(old_phone):
                    record.edit_phone(old_phone, new_phone)    
                    book.update_record(record)
                    print('Phone updated')
                else:
                    print('Phone not found')
            except ValueError:
                print('Enter name and phones')
            except FieldValidationException as e:
                print(str(e))
        elif command == "phone":
            try:    
                record = book.find(args[0])
                if record is None:
                    print('Contact not found')
                else:
                    print(record.show_phones())
            except IndexError:
                print('Enter name')
        elif command == "all":
            all = book.get_all()
            for name, record in all.items():
                print(f"{name.capitalize()}: {record.show_phones()}")
        elif command == "add-birthday":
            try:
                name, date = args
                record = book.find(name)
                if record is None:
                    print('Contact not found')
                else:
                    record.add_birthday(date)
                    book.update_record(record)
                    print('Birthday added')
            except FieldValidationException as e:
                print(str(e))
            except ValueError:
                print('Enter name and birthday')
        elif command == "show-birthday":
            try:
                record = book.find(args[0])
                if record is None:
                    print('Contact not found')
                else:
                    print(record.show_birthday())
            except IndexError:
                print('Enter name')
        elif command == "birthdays":
            book.get_birthdays_per_week()
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
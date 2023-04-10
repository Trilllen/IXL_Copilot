import configparser
import tkinter as tk
import customtkinter as ctk


class SettingsManager:
    """
    A class for managing application settings.

    Attributes:
        settings_file (str): The path to the settings file.
        key (str): The key used for obfuscating sensitive data.
        settings (configparser.ConfigParser): The configparser with the current settings.
    """
    def __init__(self):
        self.settings_file = "settings.ini"
        self.key = '😊😂😁😁🙌😂👀😃🤢😆🐱‍🐉'
        self.settings = self.load_settings()

    def save_settings(self):
        """
        Save the current settings to the settings file.

        Returns:
            None
        """
        # Obfuscate only the username and password
        for section in self.settings.sections():
            if self.settings.has_option(section, 'username'):
                username = self.settings.get(section, 'username')
                obfuscated_username = self.xor_encode(username)
                self.settings.set(section, 'username', obfuscated_username)

            if self.settings.has_option(section, 'password'):
                password = self.settings.get(section, 'password')
                obfuscated_password = self.xor_encode(password)
                self.settings.set(section, 'password', obfuscated_password)

        with open(self.settings_file, 'w') as settings_file:
            self.settings.write(settings_file)

    def load_settings(self):
        """
        Load the settings from the settings file.

        Returns:
            configparser.ConfigParser: The loaded settings object.
        """
        settings = configparser.ConfigParser()
        settings.read(self.settings_file)

        # Deobfuscate only the username and password
        for section in settings.sections():
            if settings.has_option(section, 'username'):
                obfuscated_username = settings.get(section, 'username')
                deobfuscated_username = self.xor_decode(obfuscated_username)
                settings.set(section, 'username', deobfuscated_username)

            if settings.has_option(section, 'password'):
                obfuscated_password = settings.get(section, 'password')
                deobfuscated_password = self.xor_decode(obfuscated_password)
                settings.set(section, 'password', deobfuscated_password)

        return settings

    def xor_encode(self, value):
        """
        Obfuscate the given value using XOR encryption.

        Args:
            value (str): The value to obfuscate.

        Returns:
            str: The obfuscated value.
        """
        xor_key = self.key  # Use your own key for obfuscation
        obfuscated_chars = [ord(c) ^ ord(xor_key[i % len(xor_key)]) for i, c in enumerate(value)]

        # Convert the obfuscated characters into a comma-separated string of Unicode code points
        formatted_value = ",".join(map(str, obfuscated_chars))
        return formatted_value

    def xor_decode(self, formatted_value):
        """
        Deobfuscate the given value using XOR encryption.

        Args:
            formatted_value (str): The obfuscated value.

        Returns:
            str: The deobfuscated value.
        """
        xor_key = self.key  # Use your own key for obfuscation

        if not formatted_value or ',' not in formatted_value:
            return formatted_value  # return the value if its not correct

        # Convert the comma-separated string of Unicode code points back into obfuscated characters
        obfuscated_chars = [chr(int(x)) for x in formatted_value.split(',')]

        # XOR the obfuscated characters to obtain the original value
        original_value = ''.join(chr(ord(c) ^ ord(xor_key[i % len(xor_key)])) for i, c in enumerate(obfuscated_chars))
        return original_value

    def get_active_classes(self):
        """
        Get the names of the current active classes.

        returns:
            lst: the names of the current active classes
        """

    def get_number_of_classes(self):
        """
        Get the number of active classes.

        Returns:
            int: The number of active classes.
        """
        count = 0
        for setting in self.settings:
            # Find all Class settings and count the number of active ones.
            if not setting.startswith('Class_'):
                continue
            if self.settings.getboolean(setting, 'active'):
                count += 1
        return count

    def get_schedule(self):
        """
        Get the class schedule.

        Returns:
            list: A list of tuples, where each tuple contains the class name and its associated periods.
        """
        schedule = []
        for setting in self.settings:
            if not setting.startswith('Class_'):
                continue  # skip if we aren't looking at a class
            if not self.settings.getboolean(setting, 'active'):
                continue  # skip if the class is not turned on
            if self.settings[setting]['periods'] == '':
                schedule.append((self.settings[setting]['name'], None))  # assign no periods if we have none saves
            else:
                periods_str = self.settings[setting]['periods']
                periods = list(map(int, periods_str.split(',')))
                schedule.append((self.settings[setting]['name'], periods))
        return schedule


# Setting Frame
class SettingsFrame(ctk.CTkFrame):
    def __init__(self, window):
        super().__init__(master=window, fg_color='#572b2b')
        self.window = window
        self.relwidth = 0.23
        self.settings = SettingsManager()

        # animation logic
        self.docked = False
        self.docked_pos = 10
        self.undocked_pos = -200
        self.pos = self.undocked_pos
        self.height = 200

        # layout
        # build grid
        self.rowconfigure((0, 1), weight=1, uniform='a')
        self.columnconfigure(0, weight=1, uniform='a')

        # add widgets
        self.class_manage_button = ScheduleButton(self)
        self.login_manage_button = LoginUpdaterButton(self)

        # place widgets
        self.class_manage_button.grid(row=0, column=0, sticky='nsew', padx=10, pady=30)
        self.login_manage_button.grid(row=1, column=0, sticky='nsew', padx=10, pady=30)
        self.place(relx=0.33, y=self.pos, relwidth=self.relwidth, relheight=0.5)

    def toggle(self):
        if self.docked:
            self.window.dock = None
            self.undock()

        else:
            self.dock()

    def dock(self):
        self.docked = True
        self.window.swap_frame(self)
        self.animate()

    def undock(self):
        self.docked = False
        self.animate()

    def animate(self):
        if self.docked:
            self.dock_animation()
        else:
            self.undock_animation()

    def undock_animation(self):
        if self.pos > self.undocked_pos:
            self.pos -= 1
            self.place(relx=0.33, y=self.pos, relwidth=self.relwidth, relheight=0.5)
            self.after(1, self.animate)
        else:
            self.docked = False

    def dock_animation(self):
        if self.pos < self.docked_pos:
            self.pos += 2
            self.place(relx=0.33, y=self.pos, relwidth=self.relwidth, relheight=0.5)
            self.after(1, self.animate)
        else:
            self.docked = True


# Manage schedule
class ScheduleButton(ctk.CTkButton):

    def __init__(self, frame):
        super().__init__(frame,
                         text='Manage Schedule',
                         fg_color='#570000',
                         command=self.open_schedule)
        self.frame = frame

    def open_schedule(self):
        # Create a new top-level window
        new_window = ScheduleWindow(self.frame.window)
        new_window.deiconify()


class ScheduleWindow(ctk.CTkToplevel):
    window_open = False

    def __init__(self, master):
        if not ScheduleWindow.window_open:
            ScheduleWindow.window_open = True
            super().__init__(master)
            self.master = master
            self.geometry("400x300")
            self.title("Schedule Manager")
            self.resizable(False, False)
            self.attributes("-topmost", True)

            # load our settings
            self.settings = SettingsManager()
            self.classes = []

            # Closing the window sets window_open back to False
            self.protocol("WM_DELETE_WINDOW", self.on_close)

        # layout
        self.columnconfigure(0, weight=2)
        self.columnconfigure((1, 2, 3, 4, 5, 6), weight=1)
        self.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1, uniform='a')

        # header row
        class_name_label = ctk.CTkLabel(self, text='Class name')
        class_name_label.grid(row=0, column=0, padx=5)

        for period in range(1, 7):
            period_label = ctk.CTkLabel(self, text=f'Per {period}')
            period_label.grid(row=0, column=period)

        # Make and place the Add/remove button

        # Find the row we need to place our button in and place it
        add_button_row = self.settings.get_number_of_classes() + 1
        add_remove_frame = self.add_remove_buttons()
        add_remove_frame.grid(row=add_button_row, column=0, )

        # next fill out our classes

        schedule = self.settings.get_schedule()
        for i, classroom in enumerate(schedule):
            self.classes.append(ClassWidget(classroom[0], classroom[1], i + 1, self))

        # Make and place the save button
        self.save_frame = ctk.CTkFrame(self, fg_color='#242424')
        self.save_frame.grid(row=8, column=0, columnspan=7, sticky='nsew')
        save_button = ctk.CTkButton(self.save_frame,
                                    text='save',
                                    command=self.save)
        save_button.pack()

    def add_remove_buttons(self):
        frame = ctk.CTkFrame(self,
                             width=100,
                             height=20)
        frame.columnconfigure((0, 1), weight=1, uniform='a')
        frame.rowconfigure(0, weight=1)
        self.add_button = ctk.CTkButton(frame,
                                        text='+',
                                        font=('', 20),
                                        border_spacing=0,
                                        fg_color='green',
                                        hover_color='#00aa00',
                                        width=45,
                                        command=lambda: self.add_class(frame))
        self.add_button.grid(row=0, column=0)
        self.remove_button = ctk.CTkButton(frame,
                                           text='-',
                                           font=('', 20),
                                           border_spacing=0,
                                           fg_color='red',
                                           width=45,
                                           command=lambda: self.remove_class(frame)
                                           )
        self.remove_button.grid(row=0, column=1)
        return frame

    def add_class(self, frame):
        new_class_index = self.settings.get_number_of_classes() + 1
        self.settings.settings.set(f'Class_{new_class_index}', 'active', 'True')
        self.classes.append(ClassWidget('', None, new_class_index, self))
        frame.grid(row=new_class_index + 1, column=0)

        # Disable the add button when there are 6 classes made
        if len(self.classes) >= 6:
            self.add_button.configure(state=tk.DISABLED)

    def remove_class(self, frame):
        if self.classes:  # Make sure there are classes to remove
            class_to_remove = self.classes.pop(-1)
            class_index = len(self.classes) + 1

            # Set the active setting to False
            self.settings.settings.set(f'Class_{class_index}', 'active', 'False')

            # Remove the class widget from the schedule window
            class_to_remove.name_box.grid_remove()
            for box in class_to_remove.boxes:
                box.grid_remove()

            # Remove the class widget from the active_classes list
            ClassWidget.active_classes.remove(class_to_remove)

            # Move the add/remove buttons frame up a slot
            frame.grid(row=class_index, column=0)

            # Enable the add button if there are less than 6 classes
            if len(self.classes) < 6:
                self.add_button.configure(state=tk.NORMAL)

    def save(self):
        for class_number, class_object in enumerate(self.classes):
            class_number += 1  # we didn't start at but we probably should have
            name = class_object.name_box.get()
            periods = []
            for period, box in enumerate(class_object.boxes):
                period += 1
                if bool(box.get()):
                    periods.append(period)

            # Update the settings object with the new name and periods
            self.settings.settings.set(f'Class_{class_number}', 'name', name)
            self.settings.settings.set(f'Class_{class_number}', 'periods', ','.join(map(str, periods)))

        # clear any of our classes that we got rid of
        for class_number in range((len(self.classes)) + 1, 7):
            self.settings.settings.set(f'Class_{class_number}', 'active', 'False')
            self.settings.settings.set(f'Class_{class_number}', 'name', '')  # clear the name
            self.settings.settings.set(f'Class_{class_number}', 'periods', '')  # clear the periods

        # Save the updated settings to the settings file
        self.settings.save_settings()
        self.on_close()

    def on_close(self):
        ClassWidget.active_classes.clear()  # destroy our stuff so we don't get errors if we reopen it
        ScheduleWindow.window_open = False
        self.destroy()


class ClassWidget:  # holds the info and logic for each class we have
    active_classes = []

    def __init__(self, name, periods, row, parent):
        self.name = name
        self.periods = periods
        self.parent = parent
        self.row = row
        self.name_box = self.name_box()
        self.boxes = self.build_check_boxes()
        ClassWidget.active_classes.append(self)

    def name_box(self):
        name_box = ctk.CTkEntry(self.parent)
        name_box.insert(0, self.name)
        name_box.grid(row=self.row, column=0)
        return name_box

    def build_check_boxes(self):  # build our checkbox
        boxes = []
        for period in range(1, 7):
            box = ctk.CTkCheckBox(self.parent,
                                  text='',
                                  width=20,
                                  command=lambda p=period: self.toggle_checkbox(p))
            if self.periods is not None:
                if period in self.periods:
                    box.select()
            box.grid(row=self.row, column=period)
            boxes.append(box)  # Append the box to the boxes list
        return boxes

    def toggle_checkbox(self, period):
        # Check if the box is checked, if not, ignore
        if self.boxes[period - 1].get():
            # Uncheck all other boxes in the same column
            for class_widget in ClassWidget.active_classes:
                if class_widget is not self:
                    class_widget.boxes[period - 1].deselect()


# Manage Credentials
class LoginUpdaterButton(ctk.CTkButton):
    def __init__(self, frame):
        super().__init__(frame,
                         text='Update Logins',
                         fg_color='#570000',
                         command=self.open_login_updater)
        self.frame = frame

    def open_login_updater(self):
        # open the window if it's not already open
        if not LoginUpdaterWindow.window_open:
            new_window = LoginUpdaterWindow(self.frame.window)
            new_window.deiconify()


class LoginUpdaterWindow(ctk.CTkToplevel):
    window_open = False

    def __init__(self, master):
        LoginUpdaterWindow.window_open = True
        super().__init__(master)
        self.master = master
        self.geometry("250x200")
        self.title("Login Updater")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        # load our settings
        self.settings = SettingsManager()

        # build widgets
        self.website_selection_widget = self.website_selection_box()
        username_label = ctk.CTkLabel(self, text='Username')
        self.username_entry = ctk.CTkEntry(self)
        password_label = ctk.CTkLabel(self, text='Password')
        self.password_entry = ctk.CTkEntry(self)
        save_button = ctk.CTkButton(self, text='Save', command=self.save)

        # set up our layout
        self.columnconfigure((0, 1), weight=0)
        self.rowconfigure((0, 1, 2, 3), weight=0, uniform='a')

        # place widgets
        self.website_selection_widget.grid(row=0, column=1)
        username_label.grid(row=1, column=0, sticky='e', padx=10)
        self.username_entry.grid(row=1, column=1, padx=10, pady=10)
        password_label.grid(row=2, column=0, sticky='e', padx=10)
        self.password_entry.grid(row=2, column=1, padx=10, pady=10)
        save_button.grid(row=3, column=1, padx=10, pady=10)

        # Closing the window sets window_open back to False
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def website_selection_box(self):
        # get our options
        websites = []
        for section in self.settings.settings.sections():
            if self.settings.settings.has_option(section, 'password'):
                websites.append(self.settings.settings.get(section, 'name'))
        box = ctk.CTkComboBox(self,
                              values=websites)
        return box

    def save(self):
        # grab our parameters
        website = self.website_selection_widget.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        # grab the section we are saving to
        for section in self.settings.settings.sections():
            if self.settings.settings.has_option(section, 'name'):
                if self.settings.settings.get(section, 'name') == website:
                    self.settings.settings.set(section, 'username', username)
                    self.settings.settings.set(section, 'password', password)
                    break
        self.settings.save_settings()

        # Close after we save
        # don't change unless you resolve issue of things saving unscrambled if you save a second thing
        self.on_close()

    def on_close(self):
        LoginUpdaterWindow.window_open = False
        self.destroy()



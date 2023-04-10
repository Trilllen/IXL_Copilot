import threading
import customtkinter as ctk
import tkcalendar
import CopilotAddIXLSkill
import CopilotSettings
import TeacherTools

"""
When you create a .exe on Windows with pyinstaller, there are two things you have to consider. Firstly, you cannot use
the --onefile option of pyinstaller, because the customtkinter library includes not only .py files, but also data files
like .json and .otf. PyInstaller is not able to pack them into a single .exe file, so you have to use the --onedir 
option.
And secondly, you have to include the customtkinter directory manually with the --add-data option of pyinstaller. 
Because for some reason, pyinstaller doesn't automatically include datafiles like .json from the library. 
You can find the install location of the customtkinter library with the following command:
"""  # notes about packaging

"""
Main Window
"""


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.dock = None
        self.title('IXL Co-Pilot')
        self.geometry('600x400')
        self.resizable(False, False)

        #widgets
        self.add_frame = CopilotAddIXLSkill.AddSkillFrame(self)
        self.main_frame = MainFrame(self)


        #Place widgets
        self.main_frame.place(x=10, y=10, relwidth=0.3, relheight=.5)

    def swap_frame(self, frame):
        if self.dock is not None:  # undock our current frame if we have one
            self.dock.undock()
        self.dock = frame


class MainFrame(ctk.CTkFrame):

    def __init__(self, window):
        super().__init__(window)

        # save the window for when we need to ref it later
        self.window = window

        # layout
        self.rowconfigure((0, 1, 2), weight=1, uniform='a')
        self.columnconfigure(0, weight=1)

        # build the widgets
        self.update_button = self.build_update_button()
        self.add_skill_button = self.build_add_skill_button()

        # place the widgets
        self.update_button.grid(row=0, column=0, sticky='nsew', padx=30, pady=20)
        self.add_skill_button.grid(row=1, sticky='nsew', padx=30, pady=20)

    def build_update_button(self):
        button = ctk.CTkButton(
            self,
            text='Update IXL scores',
            fg_color='#69C130',
            text_color='#000',
            hover_color='#7DE739',
            command=self.update_button_action)
        return button

    def build_add_skill_button(self):
        button = ctk.CTkButton(
                self,
                text='Add IXL Skill',
                text_color='#000',
                fg_color='#1797E0',
                hover_color='#18A7F9',
                command=self.window.add_frame.toggle)

        return button

    def update_button_action(self):
        update_thread = threading.Thread(target=TeacherTools.update_skyward_with_IXL_scores)
        update_thread.start()




def main_app():
    window = MainWindow()

    # create the settings
    settings_frame = CopilotSettings.SettingsFrame(window)

    # create the settings button
    setting_button = ctk.CTkButton(
        window.main_frame,
        text='Settings',
        text_color='#000',
        fg_color='#D22D2C',
        hover_color='#F83534',
        command=settings_frame.toggle
    )

    setting_button.grid(row=2, sticky='nsew', padx=30, pady=20)

    window.mainloop()


if __name__ == "__main__":
    main_app()

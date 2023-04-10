import TeacherTools
from typing import NamedTuple
import csv
import CopilotSettings
import customtkinter as ctk
import tkcalendar
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Skill(NamedTuple):
    classroom: str
    grade_level: str
    skill_letter: str
    skill_number: int


class AddSkillFrame(ctk.CTkFrame):

    def __init__(self, window):
        super().__init__(master=window, fg_color='#2b4757')

        # saves the window we are in for when we need to ref it
        self.window = window

        # load our information
        self.skill_options = get_skill_master_list()

        # build variables
        self.class_var = ctk.StringVar()
        self.grade_level_var = ctk.StringVar()
        self.skill_letter_var = ctk.StringVar(value='')
        self.skill_number_var = ctk.StringVar(value='')

        # layout
        self.rowconfigure((0, 1, 2, 3, 4), weight=1, uniform='a')
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)

        # build the widgets
        class_label = ctk.CTkLabel(self, text='Class')
        self.class_box = self.build_class_box()
        grade_level_label = ctk.CTkLabel(self, text=' Skill Grade Level ')
        self.grade_level_box = self.build_grade_level_box()
        skill_letter_label = ctk.CTkLabel(self, text='Skill Letter')
        self.skill_letter_box = self.build_letter_box()
        skill_number_label = ctk.CTkLabel(self, text='Skill Number')
        self.skill_number_box = self.build_number_box()
        assigned_date_label = ctk.CTkLabel(self, text='Date Assigned')
        self.assigned_date_button = tkcalendar.DateEntry(self)
        self.confirmation_label = ctk.CTkLabel(self, text='',)
        self.run_button = self.build_run_button()

        # place the widgets
        class_label.grid(row=0, column=0)
        self.class_box.grid(row=0, column=1)
        grade_level_label.grid(row=1, column=0)
        self.grade_level_box.grid(row=1, column=1)
        skill_letter_label.grid(row=2, column=0)
        self.skill_letter_box.grid(row=2, column=1)
        skill_number_label.grid(row=3, column=0)
        self.skill_number_box.grid(row=3, column=1)
        assigned_date_label.grid(row=4, column=0)
        self.assigned_date_button.grid(row=4, column=1)
        self.run_button.grid(row=2, column=2, sticky='nsew', padx=20, pady=10)

        # animation logic
        self.docked = False
        self.docked_pos = 10
        self.undocked_pos = -200
        self.pos = self.undocked_pos
        self.height = 200

        # placement
        self.place(relx=0.33, y=self.pos, relwidth=0.48, relheight=0.5)

    # widget construction
    def build_class_box(self):

        # load the available classes from settings
        settings = CopilotSettings.SettingsManager()
        schedule = settings.get_schedule()
        classes = [classroom[0] for classroom in schedule]

        # only try and fill the field if we have something to fill it with
        if len(classes) > 0:
            self.class_var.set(classes[0])  # define our classroom groups

        # build the box
        box = ctk.CTkComboBox(
            self,
            values=classes,
            variable=self.class_var,
            width=100)
        return box

    def build_grade_level_box(self):
        grade_level_options = self.skill_options.keys()

        box = ctk.CTkComboBox(
            self,
            values=grade_level_options,
            variable=self.grade_level_var,
            command=self.change_letter_options,
            width=60)

        return box

    def build_letter_box(self):
        box = ctk.CTkComboBox(
            self,
            variable=self.skill_letter_var,
            command=self.change_number_options,
            values=[],
            width=60)

        return box

    def build_number_box(self):
        box = ctk.CTkComboBox(
            self,
            variable=self.skill_number_var,
            command=self.update_confirmation_label,
            values=[],
            width=60)

        return box

    def build_run_button(self):
        button = ctk.CTkButton(
                self,
                text='Run',
                fg_color='#5e7350',
                text_color='#000',
                hover_color='#7DE739',
                state='disabled',
                command=self.run)
        return button

    # widget commands
    def change_letter_options(self, choice):
        """get the keys that ar associated with our current choice they will be unsorted. So we should sort them, since
         we get them as a tuple we need to turn them into a list before sorting"""
        skill_letter_options = sorted(list(self.skill_options[choice].keys()))
        self.skill_letter_box.configure(values=skill_letter_options)

    def change_number_options(self, choice):
        # get the keys that are associated with our current choice of both grade_level letter and number. They will be
        # unsorted so we'll sort them. Since we get them as a tuple we need to turn them into a list before sorting
        skill_number_max = self.skill_options[self.grade_level_var.get()][choice]
        number_options = [str(i) for i in range(1, skill_number_max + 1)]
        self.skill_number_box.configure(values=number_options)
        self.update_confirmation_label(None)  # update our confirmation box

    def update_confirmation_label(self, _):
        self.run_button.configure(fg_color='#7DE739', state="normal")

        if self.grade_level_var.get() and self.skill_letter_var.get():
            self.confirmation_label.configure(
                text=f"Add {self.grade_level_var.get()} {self.skill_letter_var.get()}.{self.skill_number_var.get()}\n to {self.class_var.get()}")

    def run(self):
        date = self.assigned_date_button.get_date()
        date_str = date.strftime('%m%d%Y')
        classroom = self.class_var.get()
        grade_level = self.grade_level_var.get()
        skill_letter = self.skill_letter_var.get()
        skill_number = int(self.skill_number_var.get())
        skill = Skill(classroom, grade_level, skill_letter, skill_number)
        add_skill(skill, date_str)

    # animation control
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
            self.place(relx=0.33, y=self.pos, relwidth=0.48, relheight=0.5)
            self.after(1, self.animate)
        else:
            self.docked = False

    def dock_animation(self):
        if self.pos < self.docked_pos:
            self.pos += 2
            self.place(relx=0.33, y=self.pos, relwidth=0.48, relheight=0.5)
            self.after(1, self.animate)
        else:
            self.docked = True


def get_skill_master_list():  # returns our nested dictionary
    with open("skill_master_listV2.txt") as csvfile:
        reader = csv.reader(csvfile)
        skill_options = {}
        for row in reader:
            # assign our grade_level level
            grade_level = row[0]
            skill_options[grade_level] = {}  # initialize our empty dictionary

            for item in row[1:]:
                skill_letter, max_skill_number = item.rsplit('.')
                skill_options[grade_level][skill_letter] = int(max_skill_number)
    return skill_options


def csv_to_scoredict(file):  # takes the csv file and turns it into our dict of scores
    scores = dict()
    with open(file, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            name = parts[0].strip() + ', ' + parts[1].strip()
            scores[name] = int(parts[2])
    return scores


def create_in_skyward(skill, due_date, driver):
    driver.switch_to.window(driver.window_handles[1])
    driver.get("https://www.q.wa-k12.net/auburn/Gradebook/GradebookBySection/AssignmentListSections")
    wait = WebDriverWait(driver, 10)

    # get our schedule
    settings = CopilotSettings.SettingsManager()
    schedule = settings.get_schedule()

    for classroom in schedule:
        if skill.classroom == classroom[0]:
            target_period = classroom[1][0]
            remaining_periods = classroom[1][1:]

    # click on the element contains our target period
    wait.until(EC.presence_of_element_located(
            (By.XPATH, f"//*[contains(text(), 'Period {target_period}')]"))).click()  # click on alg if we are making an algebra skill

    wait.until(
        EC.element_to_be_clickable((By.ID, "browse_newButton"))).click()  # create a new assignment

    # on the new assignment template

    # set it to practice
    wait.until(EC.element_to_be_clickable((By.ID, "AssignmentCategoryID_code"))).click()  #
    driver.switch_to.active_element.send_keys("PRAC")  # categorize as a practice assignment
    sleep(1)
    driver.switch_to.active_element.send_keys(Keys.ENTER)

    # set the date assigned
    assigned_date_field = driver.find_element(By.ID, "AssignmentAssignedDate")  # set our assigned date
    assigned_date_field.send_keys(Keys.CONTROL + 'a')
    assigned_date_field.send_keys(due_date)

    # set the due date
    due_date_field = driver.find_element(By.ID, "AssignmentDueDate")  # set our assigned date
    due_date_field.send_keys(Keys.CONTROL + 'a')
    due_date_field.send_keys(due_date)

    driver.find_element(By.ID, "AssignmentName").click()
    driver.switch_to.active_element.send_keys(
        f"IXL {skill.grade_level} {skill.skill_letter}.{skill.skill_number}")  # name the skill
    driver.find_element(By.ID, "AssignmentMaxScore").clear()
    driver.find_element(By.ID, "AssignmentMaxScore").send_keys("8")  # set max score
    sleep(1)

    # attempting to fix the checkbox logic that should not be broken
    table = driver.find_element(By.ID, "SectionsToAssignTo_unlockedBody")
    rows = table.find_elements(By.TAG_NAME, "tr")
    for period in remaining_periods:
        for row in rows:
            # check if the checkbox is not disabled
            checkbox = row.find_element(By.CSS_SELECTOR, ".checkbox")
            if not checkbox.get_attribute('disabled'):
                # check if the primary period contains the number we're looking for
                potential_period = row.find_element(By.CSS_SELECTOR, 'td.column6')
                if str(period) in potential_period.text:
                    # click the checkbox
                    checkbox.click()
                    break  # stop looking once we found our target
        print(f"failed to find period{period}")
    driver.find_element(By.ID, "popup0_next").click()  # This is where we save


def add_skill(skill, due_date):
    driver = TeacherTools.set_up_window()
    #create_in_skyward(skill, due_date, driver)

    # Load our schedule and figure out what periods we need to add scores too
    settings = CopilotSettings.SettingsManager()
    schedule = settings.get_schedule()
    for class_group in schedule:  # grab the periods of our class group
        if skill.classroom == class_group[0]:
            periods = class_group[1]
            break

    for period in periods:
        # get our data for the period we are after
        raw_data = TeacherTools.get_IXL_skill_cvs(
            period, skill.grade_level, skill.skill_letter, skill.skill_number, driver)
        clean_data = TeacherTools.format_file(raw_data)
        scores = csv_to_scoredict(clean_data)
        TeacherTools.export_scores(scores, period, skill.grade_level, skill.skill_letter, skill.skill_number, driver)

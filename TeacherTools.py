from time import sleep
import csv
import os
import CopilotSettings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

home_dir = os.path.dirname(os.path.abspath(__file__))
datafolder_path = os.path.join(home_dir, "Data")


# Construct the path to the downloads directory based on the operating system
if os.name == "posix":  # Unix or Linux
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
elif os.name == "nt":  # Windows
    downloads_dir = os.path.join(os.environ["USERPROFILE"], "Downloads")
else:
    raise RuntimeError("Unsupported operating system")


class StudentScoresSky:  # a student referenced by SID that has their assignments and scores as key pairs
    students = {}  # we're making a dictionary of all the students that we have made that will be keyed with their SID

    # and the values are the student objects

    def __init__(self, name, SID, period, scores):
        self.name = name
        self.SID = SID
        self.scores = scores
        self.period = period
        StudentScoresSky.students.update({self.SID: self})  # saves the student we just made in our dict keyed with
        # their SID


class StudentScoresIXL:  # a student referenced by SID that has their assignments and scores as key pairs
    students = {}  # we're making a dictionary of all the students that we have made that will be keyed with their SID

    # and the values are the student objects

    def __init__(self, name, SID, scores):
        self.name = name
        self.SID = SID
        self.scores = scores
        StudentScoresIXL.students.update({self.SID: self})  # saves the student we just made in our dict keyed with
        # their SID


def grab_period(period):
    with open("Student_List.csv", "r") as student_list:
        reader = csv.reader(student_list)
        return_list = []
        next(reader)  # skip header
        for student in reader:
            if int(student[2]) == period:
                return_list.append(student)
        return return_list


def does_this_element_exist(element, driver):
    elements = driver.find_elements(By.CSS_SELECTOR, element)
    if len(elements) != 0:
        return True
    else:
        return False


def get_IXL_scores(csv_path, driver):
    import fnmatch
    import shutil
    driver.switch_to.window(driver.window_handles[0])  # switch to our skyward window
    driver.get('https://www.ixl.com/analytics/score-grid?#grades=7,8,20,21')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.ID, "skill-filter-active"))).click()
    sleep(1)
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "export-button-container"))).click()
    sleep(1)
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//label[text()='Gradebook view: Students in the left column']"))).click()
    sleep(1)
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "options-export-button"))).click()
    sleep(5)  # waiting for the download to finish

    pattern = "IXL-Score-Grid*"
    matching_files = fnmatch.filter(os.listdir(downloads_dir), pattern)  # filters the downloads folder
    sorted_files = sorted(matching_files, key=lambda x: os.path.getmtime(os.path.join(downloads_dir, x)), reverse=True)
    IXL_file_name = sorted_files[0]  # grab the newest possible file
    IXL_file = os.path.join(downloads_dir, IXL_file_name)
    shutil.move(IXL_file, csv_path)


def get_grade_book_csv(period, driver):
    """gets handed a period as a str and the driver to grab the skyward grade sheet csv and move it to the data folder"""
    import shutil
    browse_csv_path = os.path.join(downloads_dir, "browse.csv")
    if os.path.isfile(browse_csv_path):  # remove an old download if it got stuck there.
        os.remove(browse_csv_path)
    driver.switch_to.window(driver.window_handles[1])  # switch back to our skyward window
    driver.get('https://www.q.wa-k12.net/auburn/Gradebook/GradebookBySection/Sections')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, f"//*[contains(text(), 'Period {period}')]"))).click()  # open the grad book
    export_button_clicked = False

    # brute forcing the export button cause its not consistent, were just gonna keep clicking till it works
    while not export_button_clicked:
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@aria-label="More options"]'))).click()  # click more
            sleep(0.3)  # wait a short amount of time
            driver.find_element(By.XPATH,
                                '//a[@class="menuPopupItem" and contains(span[@class="anchorText textAfter '
                                'svgGroup"], "Export")]'
                                ).click()  # try to click export
            export_button_clicked = True
        except Exception:
            pass

    while not os.path.isfile(browse_csv_path):
        sleep(.1)
    savefolder_path = os.path.join(home_dir, "Data")
    os.makedirs(savefolder_path, exist_ok=True)  # create the subfolder if it doesn't exist
    save_spot = os.path.join(savefolder_path, f"Skyward_{period}.csv")
    shutil.move(browse_csv_path, save_spot)
    return save_spot


def format_skyward_csv(csvfile):  # creates the classes of our skyward students
    with open(csvfile, "r") as grade_book_file:
        grade_book = list(csv.reader(grade_book_file))
        period = grade_book[1][3].lstrip("Period: ")
        assignment_indexes = dict()
        for index, assignment in enumerate(grade_book[3]):  # creates our list of assignments
            if assignment != "":  # skip all the lines that have nothing because those aren't assignments.
                assignment_indexes.update({assignment: index})
        # build our student grade_level book class
        for student in grade_book[9:]:  # the data for the students starts on the 10th row
            scores = {}

            # we are going to format the SID how we want it, with '' and nothing but numbers
            SID_raw = student[3]
            SID = ''
            for c in SID_raw:
                if c.isdigit():
                    SID += c

            for assignment in assignment_indexes.keys():  # loop through our assignments with each student
                if student[assignment_indexes[assignment]] == '*':
                    score = float(-1)  # score is -1 if ungraded so the bot will go and replace it with a 0
                else:
                    score = float(student[assignment_indexes[assignment]])  # grab their score as a float
                scores.update({assignment: score})  # assign the score to the dict keyed with its name
            StudentScoresSky(student[1], student[3], period, scores)


def format_big_IXL_cvs(csvfile):  # MUST BE IMPORTED AS GRADE SHEET
    with open(csvfile, "r") as IXL_file:
        IXL_list = list(csv.reader(IXL_file))

        # grab the assignments from the file and format them the way we use them internally
        grade_level_row = IXL_list[0]
        skill_code_row = IXL_list[2]

        # building our list of IXL skills
        IXL_skills = []
        for assignment in range(2, len(grade_level_row)):  # grab and format the grade_level level of each skill
            if grade_level_row[assignment] == "Algebra 1":  # parse the grade_level and return our abbreviated GL code
                grade_level = "A1"
            elif grade_level_row[assignment] == "Geometry":
                grade_level = "G"
            elif grade_level_row[assignment] == "Seventh grade":
                grade_level = "7"
            elif grade_level_row[assignment] == "Eighth grade":
                grade_level = "8"
            else:
                print(grade_level_row[assignment])
                continue  # this shouldn't need to happen but it seems to so lets skip instead of getting an error
            IXL_skills.append(f'IXL {grade_level} {skill_code_row[assignment]}')

        for student in range(5, len(IXL_list)):  # slice the list for our students
            scores = {}
            # we are going to format the SID the way we want to use it with a '' and just numbers
            student_row = IXL_list[student]
            SID_raw = IXL_list[student][0]
            SID = ''
            for c in SID_raw:
                if c.isdigit():
                    SID += c
            name = IXL_list[student][1]

            # format the students scores
            for index, skill in enumerate(IXL_skills):
                if student_row[index + 2] == '':  # set score to
                    score = float(0)
                else:
                    score = int(student_row[index + 2]) / 10
                scores.update({skill: score})
            # create the student object
            StudentScoresIXL(name, SID, scores)


def get_IXL_skill_cvs(period, grade, skill_letter, skill_number,
                      driver):  # gets the IXL file, will overwrite so load the old data first if you need it
    from time import sleep
    import os
    import shutil
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    wait = WebDriverWait(driver, 10)
    driver.switch_to.window(driver.window_handles[0])
    sleep(0.5)
    driver.get('https://www.ixl.com/analytics/skill-score-chart')
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "roster-class-select-container"))).click()

    driver.find_element(by="xpath",
                        value=f"//*[contains(text(), '- {period}')]").click()  # click on the current period

    driver.find_element(by="class name", value="skill-picker-container").click()  # click on the skill list

    driver.find_element(by="xpath", value="//*[contains(text(), 'Grades')]").click()  # click on grade_level level

    # parse grade_level level and click on the correct element
    if grade == 'A1':
        driver.find_element(by="xpath", value="//*[contains(text(), 'Alg 1')]").click()
    elif grade == 'G':
        driver.find_element(by="xpath", value="//*[contains(text(), 'Geo')]").click()
    else:
        driver.find_element(by="xpath",
                            value=f'//span[@class="option-name" and text()="{grade}"]/ancestor::div[@role="button"]'
                            ).click()

    # send the skill letter
    driver.find_element(by="xpath", value=f"//*[contains(text(), '{skill_letter}.')]").click()

    # send the skill number
    driver.find_element(by="xpath", value=f"//*[contains(text(), '{skill_number}.')]").click()
    sleep(1)
    # export the data
    driver.find_element(by="class name", value="img-export").click()
    sleep(5)

    """
    File Downloaded, Now lets move it out of downloads and into our folder and give it a better name
    """
    # specify the directory where the downloads are stored

    # get a list of all the files in the directory
    files = os.listdir(downloads_dir)

    # sort the list of files by modification time in descending order
    files.sort(key=lambda x: os.path.getmtime(os.path.join(downloads_dir, x)), reverse=True)

    # get the name of the most recently downloaded file
    target_file = os.path.join(downloads_dir, files[0])
    # move it out of downloads and into our save directory
    new_spot = os.path.join(datafolder_path, target_file[len(downloads_dir) + 1:])
    shutil.move(target_file, new_spot)

    new_name = f"IXL_per{period}_{grade}_{skill_letter}.{str(skill_number)}.txt"
    new_file = os.path.join(datafolder_path, new_name)
    # check if a file already exists with the new name
    if os.path.exists(new_file):
        # if it does, remove it
        os.remove(new_file)
    # rename our file
    os.rename(new_spot, new_file)
    driver.switch_to.window(driver.window_handles[-1])  # close the new window made by the download
    driver.close()
    return new_file


def login_IXL(driver):
    from time import sleep

    #load our settings and grab our credentials
    settings = CopilotSettings.SettingsManager()
    username_IXL = settings.settings.get('IXL_Credentials', 'username')
    password_IXL = settings.settings.get('IXL_Credentials', 'password')

    driver.get('https://www.ixl.com/signin/auburnsd')
    sleep(0.5)
    driver.find_element(by="id", value="siusername").send_keys(username_IXL)
    driver.find_element(by="id", value="sipassword").send_keys(password_IXL)
    driver.find_element(by="id", value="custom-signin-button").click()


def login_skyward(driver):

    settings = CopilotSettings.SettingsManager()
    username_Sky = settings.settings.get('Skyward_Credentials', 'username')
    password_Sky = settings.settings.get('Skyward_Credentials', 'password')
    driver.get("https://www.q.wa-k12.net/auburnSTS/Session/Signin")
    driver.find_element(by='id', value='UserName').send_keys(username_Sky)
    driver.find_element(by='id', value='Password').send_keys(password_Sky)
    driver.find_element(By.CLASS_NAME, "formContainer__submitButton").click()


def set_up_window():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    driver_path = os.path.join(home_dir,'chromedriver.exe')
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)
    login_IXL(driver)
    # open a new tab and switch to it
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    login_skyward(driver)
    driver.switch_to.window(driver.window_handles[0])
    return driver


def format_file(file):
    with open(file, "r+") as scores:
        scores.readline()  # we want to skip the title lines
        lines = scores.readlines()  # read the lines
        scores.seek(0)  # go back to the start
        for line in lines:  # reads each line after the first one
            if ',' in line:  # not sure if i wrote this or GPT made this up, leaving alone for now guess is its error catching
                parts = line.split(',')  # breaks the csv into parts
                name = parts[1].strip() + ', ' + parts[2].strip()  # reorders the names and strips out an added ", "
                if len(parts) >= 4 and parts[3].strip():  # if we have a score here, save it
                    grade = int(parts[3].strip())
                else:
                    grade = 0  # if we only have a name now then their did not answer anything and get a 0
                scores.write(name + ',' + str(grade) + '\n')  # write the new score
        scores.truncate()
    return file


def export_scores(scores, period, gradelevel, skill_letter, skill_number,
                  driver):  # scores should be a dictionary of names with their scores as their key pair
    from time import sleep
    wait = WebDriverWait(driver, 10)
    driver.switch_to.window(driver.window_handles[1])
    sleep(0.5)
    driver.get("https://www.q.wa-k12.net/auburn/Gradebook/GradebookBySection/AssignmentListSections")
    sleep(1)
    driver.find_element(By.XPATH, f"//*[contains(text(), 'Period {period}')]").click()
    sleep(1)
    # Find the column that has the assignment name we are looking for
    td_element = driver.find_element(by="xpath",
                                     value=f"//td[contains(., 'IXL {gradelevel} {skill_letter}.{skill_number}')]")
    # Get the row number from the data-row attribute of the IXL we want to grade_level
    row_number = td_element.get_attribute("data-row")
    driver.find_element(by="id", value="browse_primary" + str(row_number) + "_lockedMirror").click()
    sleep(1)
    driver.find_element(by="id", value="tabScoreEntry").click()
    sleep(4)
    # horray we should be on the correct page now
    for name in scores:  # now lets try and import the scores
        points = int(scores[name]) / 10
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f'//td[contains(., "{name}")]')))  # wait untill the student is loaded
        element = driver.find_element(By.XPATH, f'//td[contains(., "{name}")]')  # find the student via SID
        data_row = element.get_attribute("data-row")  # find the row they are in
        data_row_element = driver.find_element(By.CSS_SELECTOR,
                                               f"[data-row='{data_row}']")  # select the row that the student is in
        data_row_element.find_element(By.CSS_SELECTOR,
                                      "[data-fieldname='Score']").click()  # click on the score field        driver.switch_to.active_element.send_keys(str(points))
        driver.switch_to.active_element.send_keys(str(points))
        driver.switch_to.active_element.send_keys(Keys.ARROW_DOWN)
        driver.switch_to.active_element.send_keys(Keys.ARROW_UP)
    sleep(.1)


def update_score(period, assignment, SID, score, driver):
    driver.switch_to.window(driver.window_handles[1])  # switch to our skyward window
    driver.get('https://www.q.wa-k12.net/auburn/Gradebook/GradebookBySection/AssignmentListSections')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), 'Period {period}')]"))).click()

    # grab the row of our assignment
    td_element = wait.until(EC.presence_of_element_located((By.XPATH, f"//td[contains(., '{assignment}')]")))
    row_number = td_element.get_attribute("data-row")
    wait.until(EC.element_to_be_clickable((By.ID, f"browse_primary{row_number}_lockedMirror"))).click()

    wait.until((EC.element_to_be_clickable((By.ID, 'tabScoreEntry')))).click()
    # find the row that the student is in  by SID
    wait.until(EC.presence_of_element_located((By.XPATH,
                                               "//a[contains(@class, 'gradebookAnalytics') and contains(@onclick, 'GradebookAnalytics')]")))  # wait untill we can start entering scores

    wait.until(
        EC.presence_of_element_located((By.XPATH, f'//td[contains(., "{SID}")]')))  # wait untill the student is loaded
    element = driver.find_element(By.XPATH, f'//td[contains(., "{SID}")]')  # find the student via SID
    data_row = element.get_attribute("data-row")  # find the row they are in
    data_row_element = driver.find_element(By.CSS_SELECTOR,
                                           f"[data-row='{data_row}']")  # select the row that the student is in
    data_row_element.find_element(By.CSS_SELECTOR, "[data-fieldname='Score']").click()  # click on the score field

    driver.switch_to.active_element.send_keys(str(score))  # type the score
    driver.switch_to.active_element.send_keys(Keys.ARROW_DOWN)  # leave the field so skyward saves
    sleep(.5)  # wait to be sure that skyward saved


def update_skyward_with_IXL_scores():  # used to develop tools should not run on live code
    driver = set_up_window()
    savefolder_path = os.path.join(home_dir, "Data")
    os.makedirs(savefolder_path, exist_ok=True)
    IXL_csv_path = os.path.join(savefolder_path, "IXL_Score_Grid.csv")  # define where we will save the IXL file
    get_IXL_scores(IXL_csv_path, driver)  # download the file
    format_big_IXL_cvs(IXL_csv_path)  # Parse the file to build our student objects

    # get the periods we will need to update
    settings = CopilotSettings.SettingsManager()
    schedule = settings.get_schedule()
    periods = []
    for class_group in schedule:
        for period in class_group[1]:
            periods.append(period)

    for period in periods:  # grab the current scores from skyward and build our student objects
        gradebook_csv_path = os.path.join(savefolder_path, f"Skyward_{period}.csv")
        get_grade_book_csv(period, driver)  # DOWNLOAD the file
        format_skyward_csv(gradebook_csv_path)
    # now we grab and format the IXL file

    scores_to_update = []
    # start comparing our scores
    for student in StudentScoresSky.students.values():
        if student.SID not in StudentScoresIXL.students.keys():
            continue  # skip if the student isn't in both dicts. Caused by withdrawn students
        for assignment in student.scores.keys():
            if assignment not in StudentScoresIXL.students[student.SID].scores.keys():
                continue  # skip the assignment if it's not an IXL assignment
            current_score = student.scores[assignment]  # grabs the current score in the grade_level book
            IXL_score = StudentScoresIXL.students[student.SID].scores[assignment]  # grabs the current IXL score
            if current_score < IXL_score:
                scores_to_update.append((student.period, assignment, student.SID, IXL_score))
    for assignment in scores_to_update:
        update_score(*assignment, driver)  # update all the scores we flagged for updating


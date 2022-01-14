import calendar
import time
import uuid
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from enums import FitStarKursTyp
from exceptions import NotYetBookable, KnowElementError


class Participant:
    id = uuid.UUID
    firstname = ''
    lastname = ''
    email = ''
    mobile = ''

    def __init__(self, firstname, lastname, email, mobile):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.mobile = mobile


class Booking:
    logger, driver, course_datetime = [None] * 3
    course_participants = [None]

    def __init__(self, logger, path_to_driver, headless, course_datetime, course_participants):
        self.logger = logger
        self.course_datetime = course_datetime
        self.course_participants = course_participants
        self.path_to_driver = path_to_driver
        self.headless = headless

    def create_driver(self, path_to_driver, headless):
        self.logger.debug("Creating webdriver")
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('headless')
            self.logger.debug("Webdriver option 'headless' is set")
        # options.add_experimental_option('w3c', False)
        return webdriver.Chrome(executable_path=path_to_driver, options=options)

    def book(self):
        for participant in self.course_participants:

            is_time = self.course_datetime - timedelta(days=1) < datetime.now()
            while not is_time:
                self.logger.info("Its not time yet for %s. Trying again in 10s", self.course_datetime)
                time.sleep(10)
                is_time = self.course_datetime - timedelta(days=1) < datetime.now()

            is_booked = self.bookSingleSessionSingleUser(self.course_datetime, participant)
            while not is_booked:
                is_booked = self.bookSingleSessionSingleUser(self.course_datetime, participant)

            self.logger.info("[debug] Booking session for user %s successful" % participant.firstname)

    def bookSingleSessionSingleUser(self, program_datetime, participant):
        self.logger.info("Try to book session for %s", participant.firstname)
        try:
            self.driver = self.create_driver(self.path_to_driver, self.headless)
            self.driver.get("https://www.fit-star.de/kurse/kursplaene")
            self.driver.implicitly_wait(1)

            accept_tracking_xpath = '//*[@id="cf-root"]/div/div/div[2]/div[2]/div[2]/div[2]/button'
            self.driver.implicitly_wait(4)
            accept_tracking_element = self.driver.find_element(By.XPATH, accept_tracking_xpath)
            # accept_tracking_element = WebDriverWait(browser, 20)\
            #     .until(EC.element_to_be_clickable((By.XPATH, accept_tracking_xpath)))
            accept_tracking_element.click()

            switch_neuhausen_xpath = '// *[ @ id = "content_wrap"] / section[2] / div / div[1] / div / ul / li[4] / a'
            self.driver.find_element(By.XPATH, switch_neuhausen_xpath).click()

            select_bodypump_xpath = '//*[@id="event_name"]'
            select_bodypump_element = self.driver.find_element(By.XPATH, select_bodypump_xpath)
            select_bodypump_element.click()
            select_bodypump_select_object = Select(select_bodypump_element)
            select_bodypump_select_object.select_by_index(FitStarKursTyp.Les_Mills_BODYPUMP.value)

            try:
                select_date_xpath = '//div[@aria-label="' + f'{program_datetime.day:02d}' + '.' + f'{calendar.month_name[program_datetime.month]}' + '.2022"]'
                select_date_element = self.driver.find_element(By.XPATH, select_date_xpath)
                select_date_element.click()
            except NoSuchElementException as e:
                self.logger.error('Could not find "Date" element', e)
                raise KnowElementError('Saw a know error and will exit gracefully', e)

            try:
                select_time_xpath = '//span[@aria-label="' + f'{program_datetime.hour:02d}' + ':' + f'{program_datetime.minute:02d}' + '  Termin buchen"]'
                select_time_element = self.driver.find_element(By.XPATH, select_time_xpath)
                select_time_element.click()
            except NoSuchElementException as e:
                self.logger.error('Could not find "Time" element', e)
                raise KnowElementError('Saw a know error and will exit gracefully')

            # Try to fill out participant details
            try:
                fillform_gender_xpath = '//*[@id="gender"]'
                fillform_gender_element = self.driver.find_element(By.XPATH, fillform_gender_xpath)
                fillform_gender_element.click()
                fillform_gender_select_object = Select(fillform_gender_element)
                fillform_gender_select_object.select_by_index(1)

                fillform_firstname_xpath = '//*[@id="firstname"]'
                fillform_firstname_element = self.driver.find_element(By.XPATH, fillform_firstname_xpath)
                fillform_firstname_element.send_keys(participant.firstname)

                fillform_lastname_xpath = '//*[@id="lastname"]'
                fillform_lastname_element = self.driver.find_element(By.XPATH, fillform_lastname_xpath)
                fillform_lastname_element.send_keys(participant.lastname)

                fillform_mobile_xpath = '//*[@id="mobile"]'
                fillform_mobile_element = self.driver.find_element(By.XPATH, fillform_mobile_xpath)
                fillform_mobile_element.send_keys(participant.mobile)

                fillform_email_xpath = '//*[@id="email"]'
                fillform_email_element = self.driver.find_element(By.XPATH, fillform_email_xpath)
                fillform_email_element.send_keys(participant.email)

            except NoSuchElementException as e:
                self.logger.debug('Could not find element for participant details', e)

                # If unable to set participant check if we tried to early
                try:
                    text_toearly_xpath = '// *[ @ id = "b2m-booking"] / div / div[2] / div[5]'
                    text_toearly_element = self.driver.find_element(By.XPATH, text_toearly_xpath)
                    if text_toearly_element.text == "Diesen Termin können Sie erst 24 Std. vor Terminbeginn buchen.":
                        self.logger.info('We are to early. Trying again later.')
                        raise NotYetBookable()
                except NoSuchElementException as e:
                    self.logger.error('Could not find "ToEarly" element', e)
                    raise KnowElementError('Saw a know error and will exit gracefully')

            selected_program_xpath = '//*[@id="sl-1"]/span'
            selected_program_element = self.driver.find_element(By.XPATH, selected_program_xpath)
            print(selected_program_element.text)
            # TODO verify correct program
            # if selected_program_element.text != FitStarKursName.Les_Mills_BODYPUMP.name:
            #     raise WrongProgram()

            selected_datetime_xpath = '//*[@id="sl-3"]/span'
            selected_datetime_element = self.driver.find_element(By.XPATH, selected_datetime_xpath)
            print(selected_datetime_element.text)
            # TODO verify correct datetime

            submit_button_xpath = '//*[@id="submit"]'
            submit_button_element = self.driver.find_element(By.XPATH, submit_button_xpath)
            submit_button_element.click()

            try:
                summary_datetime_xpath = '/html/body/div[5]/div[1]/strong'
                summary_datetime_element = self.driver.find_element(By.XPATH, summary_datetime_xpath)
                print(summary_datetime_element.text)

                summary_program_xpath = '/html/body/div[5]/div[1]/text()[2]'
                summary_program_element = self.driver.find_element(By.XPATH, summary_program_xpath)
                print(summary_program_element.text)
            except NoSuchElementException as e:
                self.logger.error('Could not find element for summary details', e)

                # TODO check for already booked message

            self.driver.quit()
            return True
        except NotYetBookable as e:
            self.driver.quit()
            return False
        except Exception as e:
            self.logger.error('Error during booking', e)
            self.driver.quit()

    def set_cookies(self, cookies):
        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def set_cookie(self, cookie):
        self.driver.add_cookie(cookie)

    def get_cookies(self):
        return self.driver.get_cookies()

    def get_cookie(self, name):
        self.driver.get_cookie(name)

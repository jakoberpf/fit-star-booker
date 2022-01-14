import logging
import sys
import locale
import yaml

from queue import Queue
from threading import Thread

from datetime import datetime
from os import path

from booking import Booking, Participant
from db import connector

# Set local to germany
locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

# Setup project root path
sys.path.append(path.join(path.dirname(__file__), "..", ".."))
projectRootPath = path.abspath(path.dirname(__file__))

# logfilePath = path.join(projectRootPath, "logs/")
# logfileName = "server+" + datetime.now().strftime("%d-%m-%Y %H:%M:%S")
# Configure logger and get rootLogger
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

# Configure logfile logging
# fileHandler = logging.FileHandler("{0}/{1}.log".format(logfilePath, logfileName))
# fileHandler.setFormatter(logFormatter)
# rootLogger.addHandler(fileHandler)

# Configure console logging
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

# Configure drivers for chrome and firefox
DRIVER_CHROME = path.join(projectRootPath, "drivers/macOSm1/chromedriver98")
DRIVER_FIREFOX = path.join(projectRootPath, "drivers/geckodriver")
# Configure paths for cookies
COOKIES = path.join(projectRootPath, "cookies/cookies.pkl")


def header():
    print("*****************************************************")
    print("******  Welcome to the fitstar booking agent!  ******")
    print("*****************************************************")


class DownloadWorker(Thread):

    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            course = self.queue.get()
            try:
                course.book()
            finally:
                self.queue.task_done()


if __name__ == "__main__":
    rootLogger.debug("Printing Header")

    header()

    rootLogger.info("Setting up Database")

    connector.create_connection("./data.sqlite")
    # TODO Create tables if not present

    rootLogger.info("Configuring Booking Server")

    # read config file
    with open("./config.yaml", 'r') as stream:
        try:
            parsed_yaml = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # creating participants
    participants = []
    for participant in parsed_yaml["participants"]:
        participants.append(
            Participant(participant["firstname"], participant["lastname"], participant["email"], participant["phone"]))

    # creating dates
    bookings = []
    for course in parsed_yaml["dates"]:
        course_datetime = datetime.strptime(course["date"], '%d/%m/%y %H:%M')
        course_participants = []
        for participant in course["participants"]:
            new_course_participant = [p for p in participants if p.firstname == participant]
            course_participants.append(new_course_participant[0])
        new_booking = Booking(rootLogger, DRIVER_CHROME, True, course_datetime, course_participants)
        bookings.append(new_booking)

    rootLogger.info("Starting Booking Server")

    # Create a queue to communicate with the worker threads
    queue = Queue()

    # Create 8 worker threads
    for x in range(8):
        worker = DownloadWorker(queue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    # Put the tasks into the queue as a tuple
    for booking in bookings:
        rootLogger.info('Queueing {}'.format(booking))
        queue.put(booking)

    # Causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()

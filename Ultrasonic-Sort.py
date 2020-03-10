############################################################################
# Name: Norman Cook
# Date: 7/12/2019
# Description: Uses the Raspberry Pi and breadboard to control the 
#   utrasonic sound sensor. The calculated distances are stored and sorted 
#   as a collection of data.
############################################################################

import RPi.GPIO as GPIO
from time import sleep, time

# constants
DEBUG = False

SETTLE_TIME = 2
CALIBRATIONS = 5

CALIBRATION_DELAY = 1

TRIGGER_TIME = 0.00001

SPEED_OF_SOUND = 343

MEASUREMENTS = []

# set the RPi to the Broadcom pin layout
GPIO.setmode(GPIO.BCM)

# GPIO pins
TRIG = 18
ECHO = 27

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# calibrates the sensor
# technically, it returns a correction factor to use in our
# calculations
def calibrate():
    print "Calibrating..."
    # prompt the user for an object's known distance
    print "-Place the sensor a measured distance away from an object."
    known_distance = input("-What is the measured distance (cm)? ")

    # measure the distance to the object with the sensor
    # do this several time and get an average
    print "-Getting calibration measurements..."
    distance_avg = 0
    for i in range(CALIBRATIONS):
        distance = getDistance()
        if (DEBUG):
            print "--Got {}cm".format(distance)
        # keep a running sum
        distance_avg += distance
        # delay a short time before using the sensor again
        sleep(CALIBRATION_DELAY)
    # calculate the average of the distances
    distance_avg /= CALIBRATIONS
    if (DEBUG):
        print "--Average is {}cm".format(distance_avg)

    # calculate the correction factor
    correction_factor = known_distance / distance_avg
    if (DEBUG):
        print "--Correction factor is {}".format(correction_factor)

    print "Done."
    print

    return correction_factor

# uses the sensor to calculate the distance to an object
def getDistance():
    # trigger the sensor by setting it high for a short time and
    # then setting it low
    GPIO.output(TRIG, GPIO.HIGH)
    sleep(TRIGGER_TIME)
    GPIO.output(TRIG, GPIO.LOW)

    # wait for the ECHO pin to read high
    # once the ECHO pin is high, the start time is set
    # once the ECHO pin is low again, the end time is set
    while (GPIO.input(ECHO) == GPIO.LOW):
        start = time()
    while (GPIO.input(ECHO) == GPIO.HIGH):
        end = time()

    # calculate the duration that the ECHO pin was high
    # this is how long the pulse took to get from the snesor to the object
    duration = end - start
    # calculate the total distance that the pulse traveled by factoring
    # in the speed of sound (m/s)
    distance = duration * SPEED_OF_SOUND
    # the distance from the sensor to the object is half of the
    # total distance traveled
    distance /= 2
    # convert from meters to centimeters
    distance *= 100

    return distance

def bubblesort(itemlist):
    count = len(itemlist)

    while (count > 0):
        index = 0
        count -= 1
        while (index < count):
            value = itemlist[index]
            if (value > itemlist[index + 1]):
                placeholder = itemlist[index + 1]
                itemlist[index + 1] = itemlist[index]
                itemlist[index] = placeholder
            index += 1

########
# MAIN #
########
# first, allow the sensor to settle for a bit
print "Waiting for sensor to settle ({}s)...".format(SETTLE_TIME)
GPIO.output(TRIG, GPIO.LOW)
sleep(SETTLE_TIME)

# next, calibrate the sensor
correction_factor = calibrate()

# then, measure
raw_input("Press enter to begin...")
print "Getting measurements:"
while (True):
    # get the distance to an object and correct it with the corection factor
    print "-Measuring..."
    distance = getDistance() * correction_factor
    sleep(1)

    # and round to four decimal places
    distance = round(distance, 4)

    # display the distance measured/calculated
    print "--Distance measured: {}cm".format(distance)

    # store distance measured
    MEASUREMENTS.append(distance)

    # prompt for another measurement
    i = raw_input("--Get another measurement (Y/n)? ")
    # stop measuring if desirec
    if (not i in [ "y", "Y", "yes", "Yes", "YES", "" ]):    
        break


# finally, cleanup the GPIO pins
print "Done."

print "Unsorted measurements:"
print MEASUREMENTS

print "Sorted measurements:"
bubblesort(MEASUREMENTS)
print MEASUREMENTS

GPIO.cleanup()

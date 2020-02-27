#!/usr/bin/python -u
#
# hmc5883_gas_counter.py
#
# Program to read the gas counter value by using the digital magnetometer HMC5883

# Copyright 2014 Martin Kompf
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#import smbus
import time
import math
import rrdtool
import os
import re
import argparse
import RPi.GPIO as GPIO
import logging

# Global data
logger = logging.getLogger('Reed')

# Trigger level and hysteresis
trigger_level = 1000
trigger_hyst = 100
# Amount to increase the counter at each trigger event
trigger_step = 0.01

# Path to RRD with counter values
count_rrd = "%s/count.rrd" % (os.path.dirname(os.path.abspath(__file__)))

def initLogger():
    # create logger with 'spam_application'
    
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('reed.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

def initGPIO():
    # RPi.GPIO Layout verwenden (wie Pin-Nummern)
    GPIO.setmode(GPIO.BCM)
    # Pin 17 auf Input setzen, dort ist der keyence angeschlossen
    GPIO.setup(17, GPIO.IN)

# Create the Round Robin Databases
def create_rrds():
    print('Creating RRD: ' + count_rrd)
    # Create RRD to store counter and consumption:
    # 1 trigger cycle matches consumption of 0.01 m**3
    # Counter is GAUGE
    # Consumption is ABSOLUTE
    # 1 value per minute for 3 days
    # 1 value per day for 30 days
    # 1 value per week for 10 years
    # Consolidation LAST for counter
    # Consolidation AVERAGE for consumption
    try:
        rrdtool.create(count_rrd,
                       '--no-overwrite',
                       '--step', '60',
                       'DS:counter:GAUGE:86400:0:100000',
                       'DS:consum:ABSOLUTE:86400:0:1',
                       'RRA:LAST:0.5:1:4320',
                       'RRA:AVERAGE:0.5:1:4320',
                       'RRA:LAST:0.5:1440:30',
                       'RRA:AVERAGE:0.5:1440:30',
                       'RRA:LAST:0.5:10080:520',
                       'RRA:AVERAGE:0.5:10080:520')
    except Exception as e:
        logger.Error('Error ' + str(e))


# Get the last counter value from the rrd database
def last_rrd_count():
    val = 0.0
    handle = os.popen("rrdtool lastupdate " + count_rrd)
    for line in handle:
        m = re.match(r"^[0-9]*: ([0-9.]*) [0-9.]*", line)
        if m:
            val = float(m.group(1))
            break
    handle.close()
    return val

# set initial count to rrd
# example rrdtool update count.rrd N:2707.32:0
#
def write_initial_rrd_count(initCounter):
    update = "N:%f:%f" % (initCounter, 0)
    # print update
    rrdtool.update(count_rrd, update)


# Main
def main():
    initLogger()

    # Check command args
    parser = argparse.ArgumentParser(
        description='Program to read the gas counter value by using the digital magnetometer HMC5883.')
    parser.add_argument('-c', '--create', action='store_true', default=False, help='Create rrd databases if necessary')
    parser.add_argument('-m', '--magnetometer', action='store_true', default=False,
                        help='Store values of magnetic induction into mag rrd')
    parser.add_argument('-i', '--init', action='store', type=float,
                        help='set initial counter to rrd, e.g. -i 123.56')
    args = parser.parse_args()


    if args.create:
        create_rrds()

    if args.init:
        write_initial_rrd_count(args.init)

    initGPIO()

    timestamp = time.time()
    counter = last_rrd_count()
    print("restoring counter to %f" % counter)

    WasHigh = False

    try:
        while True:

            # load = 1 verhindern (die pausen unten sind nur unter bestimmten Bedingungen aktiv)
            time.sleep(0.07)

            # jetzt Gas auslesen, zuerst pruefen ob 6 anliegt
            if (WasHigh) and (GPIO.input(17) == GPIO.LOW):
                WasHigh = False
                #Gaszaehler()  # Zaehlerstand erhoehen

                counter += trigger_step
                update = "N:%f:%f" % (counter, trigger_step)
                # print update
                rrdtool.update(count_rrd, update)
                timestamp = time.time()

                time.sleep(0.5)  # Hysterese: nach einer 6 kann mindestens 0.5+0.07 sec keine weitere 6 kommen

            elif not (WasHigh) and (GPIO.input(17) == GPIO.HIGH):
                WasHigh = True
                time.sleep(0.5)  # Hysterese: wenn zurueck auf 7, kann in den naechsten 0.5+0.07 sec keine 6 erscheinen
            elif time.time() - timestamp > 3600:
                # at least on update every hour
                update = "N:%f:%f" % (counter, 0)
                # print update
                rrdtool.update(count_rrd, update)
                timestamp = time.time()
                #log.info("no update in hour, write 0")
    except expression as error:
        log.Error("exception ocurred: ".error)
    finally:
        log.info("finished")


if __name__ == '__main__':
    main()

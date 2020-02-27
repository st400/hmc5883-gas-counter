reed-gas-counter
====================

Program to monitor the consumption of gas used for heating in a household .

Prerequisites
=============

* Gas counter with a rotating magnet
* Digital 3 axis magnetometer HMC5883L
* Raspberry Pi Model A or B
* Python 2.7

dependencies
==============

* apt-get install librrd-dev libpython3-dev
* pip install setuptools
* pip3 install rrdtool


reed\_gas\_counter.py
========================

![Gas counter with magnetometer HMC5883 breakout](http://www.kompf.de/tech/images/countmag_m.jpg)

This program uses a reed contact connected to one of the GPIO pins of a Raspberry to log the revolutions of a gas meter.


*Help:* 

  ./hmc5883\_gas\_counter.py -h

*Create rrd databases:*

  ./hmc5883\_gas\_counter.py -c

*Store values of magnetic induction into mag.rrd:*

  ./hmc5883\_gas\_counter.py -m

*Normal operation:*

  ./hmc5883\_gas\_counter.py


www
===

The sub-directory *www* contains an example to produce a single web page to visualize daily, weekly, monthly, and yearly charts of consumption.

![Consumption of gas recorded over 24 hours](http://www.kompf.de/tech/images/consum-ph1.gif)

License
=======

Copyright 2014 Martin Kompf

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


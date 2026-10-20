Roadrunners – Future Engineers 2026
====
<div align="center">
  <img src="./other/Roadrunners_log_groß_trans.jpeg" width="60%" alt="Roadrunners Logo">
</div>

## Table of Contents

- [Introduction](#introduction)
    - [The Team](#the-team)
	- [Season 2026 Engineering Goals](#season-2026-engineering-goals)
- [Overview](#overview)
	- [Roadrunner Fact Sheet](#roadrunner-fact-sheet)
	- [Car Photos](#car-photos)
- [Mobility & Mechanical Design](#mobility--mechanical-design)
	- [Driving Base](#driving-base)	
    - [Steering Mechanism](#steering-mechanism)
    - [Motorization](#motorization)
	- [Controllers](#controllers)
- [Power & Sense Management](#power--sense-management)  
    - [Sensors](#sensors)
		- [LiDAR](#lidar)
		- [Cameras](#cameras)
		- [Gyro](#gyro)
	- [Power Management](#power-management)
		- [Power Consumption Check](#power-consumption-check)
		- [Power Supply](#power-supply)
		- [Power Distribution](#power-distribution)
		- [Wiring Diagram](#wiring-diagram)
- [Software Architecture & Obstacle Strategy](#software-architecture--obstacle-strategy)
- [Debugging & Testing](#debugging--testing)
- [Overall System & Engineering Decisions](#overall-system--engineering-decisions)
	- [Development Goals](#development-goals)
	- [Design Trade-Offs](#design-trade-offs)
- [Appendices](#appendices)
	- [Hardware Bill of Materials](#hardware-bill-of-materials)
	- [Software Modules](#software-modules)
	- [Resources](#resources)



# Introduction

Welcome to the GitHub hub of **Team Roadrunners**, proudly representing **Germany⚫🔴🟡** at the **WRO World Final 2026**!
This repository contains all the code, documentation, and resources for our project. We have used scoring criteria from the rulebook as headings in our documentation to make it easy to navigate through our repository.

## The Team

Paul Krohn


Ben Lüttecke



## Season 2026 Engineering Goals

We have analyzed the strengths and weaknesses of our 2025 Future Engineers car. From that, we defined the goals for this season's car.


Strengths in 2025 car:
- camera model, position and FoV require only few processing to exclude non-game field areas
- footprint size small enough to pass between obstacle and near wall with enough headroom
- min-max speed range
- IMU/Gyro stability
- LEDs for Debugging and Testing


Weaknesses in 2025 car:
- weight: too heavy for single motor
- turning radius too large
- parallel parking too often touches a pink wall
- dead angles in obstacle and wall detection too large

To improve at the weaknesses, a lot of technical decisions were necessary. As we discovered, many of them were not independent from each other and had impacts on strengths we wanted to keep.
So at various points, design trade-offs were necessary between conflicting goals. 

A major point in improvements was to use a LiDAR for sensing distances and mount it in a way that it has a free 360 degree field of view. We felt this would be helpful in solving various previous weaknesses during driving and parking. However, this goal had major implications on how to build the chassis and which electronics can be used. A detailed discussion is provided in the sections about chassis and LiDAR sensor.

We sum up all the design trade-offs and the reasons for the final decisions in detail in the section [**Overall System & Engineering Decisions**](#overall-system--engineering-decisions).

We thought a LiDAR sensor would solve a lot of our dead angle problems. However, to be useful when manoeuvring within the parking box and while driving on the parcours as well, it would ideally have a full 360 degree unblocked field of view. 

- Goal 1: Redesign chassis to support a true 360 degree FoV LiDAR

- Goal 2: Achieve better agility (smaller turning circle)

- Goal 3: Redesign Software to make use of 360 degree LiDAR

- Goal 4: Increase maximum speed

  

Apart from specific goals for this season, we have defined some general engineering rules for ourselves.

- Precision before speed  
A better precision makes it more likely to run without driving errors. So it ranks higher than running at higher speed.

- Test new ideas early  
Test early whether a new idea is helpful with prototypes. Find drawbacks as early as possible.

- Always have a backup

  


# Overview

<div align="center">
  <img src="./v-photos/rr_beauty02.png" width="50%">
</div>

## Roadrunner Fact Sheet

| Property                  | Value                                                        |
| ------------------------- | ------------------------------------------------------------ |
| Height                    | 9.5 cm                                                       |
| Width                     | 13,5 cm                                                      |
| Length                    | 18,8 cm                                                      |
| Weight                    | 572 g                                                        |
| Speed Range               | min: 0.13 m/sec  max: 1.58 m/sec                             |
| Overall power consumption | 16.2 W                                                       |
| Chassis build system      | Lego Technic  (mostly)                                       |
| Motorization              | lego-compatible motor driving rear axle, 1:1 gearbox connection, no encoder |
| Steering system           | Ackermann front  steering with differential rear axle        |
| Power Supply              | 2S 7.4V 1100 mAh Lipo Battery                                |
| Sensing system            | 2 RPI cams, 360 degree LiDAR, IMU (Gyro+Acceleration)        |
| Controller                | Raspberry Pi5 8 GB + Motor and Servo HAT                     |
| Programming               | Python                                                       |



## Car Photos
Here is an overview of our final car design. High-resolution photos can be found in [**v-photos**](./v-photos/README.md). 
<table> <tr> <td align="center">
    <img src="./v-photos/front_labels.png" width="90%"><br>Front View</td> <td align="center">
        <img src="./v-photos/back_labels.png" width="90%"><br>Back View</td> </tr> <tr> <td align="center">
            <img src="./v-photos/top_labels.png" width="90%"><br>Top View</td> <td align="center">
                <img src="./v-photos/bottom_labels.png" width="90%"><br>Bottom View</td> </tr> <tr> <td align="center">
                    <img src="./v-photos/right_labels.png" width="90%"><br>Right Side</td> <td align="center">
                        <img src="./v-photos/left_labels.png" width="90%"><br>Left Side</td> </tr> </table>




# Mobility & Mechanical Design 


The chassis of the Roadrunner is constructed in two layers: 
- the driving base consists of a rear axle block with motor and gearing and the front axle block containing the steering mechanism and servo
- the electronics layer contains controllers and sensors

Our previous roadrunner car has been built from lego technic parts and we decided to keep it that way. Lego Technic is a rather sturdy material and we have lots of technic parts from other lego robotic projects in the past. 

The alternative would have been to build the chassis in 3D-printing. However, rapid prototyping, testing new ideas, new placements, other gearings etc is faster with already pre-produced parts and later changes, e.g. for surprise rules, are easier to be applied to a lego chassis.

To be able to use a LiDAR with 360 degree FoV (goal 1 for this season, see above), 

- the LiDAR must be mounted so its sensor's plane of rotation is significantly below 10 cm wall and obstacles height

- all other chassis and electronics elements must be placed below the LiDAR sensor's plane of rotation.

  

## Driving Base

The first step in flattening the driving base was to use smaller wheels. In our previous car, we used 56x14 mm Lego Spike Prime wheels, which performed well.
This year, we used the smaller variant, the 43x14 mm Spike Prime wheels. With those, there is still enough ground clearance for a Lego motor.

<img src="./v-photos/wheels.png" width="30%">

- Advantage: new wheels have same width and grip as before but save height in axle position and overall height.
- Disadvantage: smaller wheels decrease the maximum speed and therefore contradict goal 4. 

According to rule precision before speed, this is acceptable.


### Steering Mechanism

To achieve goal 3, more agility, we tested some steering system variants.

**Steering Servo Options**

|             | Geekservo Grey 360 | MG90S Micro Servo |
| ----------- | ------------------ | ----------------- |
|             |<img src="./v-photos/Servo.jpg">|<img src="./v-photos/mg90s.jpg" width="131">|
| Voltage     |       4.8 - 6V     |   4.8 - 6V        |
| Torque      |    2 kg/cm at 5V   |   2 kg/cm at 5V   |
| Weight      |        20g         |       13.4g       |
| Form Factor |     24x24x40mm     |     23x12x29mm    |

The MG90S is a little bit lighter than the Geekservo. 
The Geekservo has a housing with lego connections, so it can be used as a structural element and combines with Lego very easily.
The MG90s requires additional structural elements to build it in, which reduces the weight advantage.
We already used the Geekservo last year and it worked well, so decision is to keep it.

**Steering Geometry**

The first step was to change the steering mechanism from a parallel steering geometry to Ackermann steering geometry.

<img src="./v-photos/Ackermann_Steering_Geometry.png">

There are two options how to build an Ackermann steering geometry, place the tie rod behind or in front of the axle.
Both options had pros and cons. To find out the best configuration for our car, we had to run realistic tests.

<img src="./v-photos/Compare_steering.png" width="70%">

Our previous car had a fixed rear axle with two motors attached to it with a gearbox (see motorization). 
In theory, to get the most out of Ackermann steering, the rear axle should have a differential.
A differential gear in the rear axle would result in tighter turning circles as it allows the inner wheel of the rear axle to turn slower than the outer wheel and therefore run a smaller circle. 
However, as space is tight and we must keep the driving base as flat as possible, this means to sacrifice a motor. 

To find out which Ackermann Configuration works best and whether it is worth to rethink the motorization, we built a minimum test driving base and ran turning performance tests. We ran each combination several times and then calculated an average value for the measured turning circle. We measured the turning circle from outer rear wheel to outer rear wheel to be sure this is the minimum space our car needs to turn around in one go.

<img src="./v-photos/Minimal_Fahrwerk.jpg" width="50%">

**Tie rod behind front axle (classic Ackermann)**

| Configuration          | Turning circle width |
| ---------------------- | -------------------- |
| fixed rear axle        | 49.5 cm              |
| with differential gear | 43 cm                |

**Tie rod in front of front axle** 

| Configuration          | Turning circle width |
| ---------------------- | -------------------- |
| fixed rear axle        | 33.5 cm              |
| with differential gear | 31.5 cm :heavy_check_mark:  |

Decision: The configuration with tie rod in front of the rear axle and differential gear is best, we build that one. 
The gained agility is worth using a differential gear.



### Motorization

The resulting driving base looks like this:

<img src="./v-photos/DB_03.jpg" width="70%">

| Driving Base dimensions |         |
| ----------------------- | ------- |
| track width front       | 11.2 cm |
| track width rear        | 12 cm   |
| wheelbase               | 9 cm    |




### Mounts for electronics

Center of gravity:


Detailed building instructions for the resulting chassis and the bill of materials can be found in [**Building_Instructions**](./Building_Instructions/README.md).


## Controllers

- previous car: separate motor controller and servo controller.
- this year: goal: use combined controller to save space and build flat enough for LiDAR
- test 3 types: adeept robot hat 3.0, waveshare robot driver hat and Seengreat motor and servo hat.
- problem: only 1 pca9685 pwm driver for both motor pwm and servo pwm.
  - servo: needs 50 Hz pwm frequency, motors: typically uses a lot higher frequency -> not possible with only 1 pwm driver
  - original lego PFL Motor rattles loudly at low speed and 50 Hz, CaDa rattles much less due to better gearing quality
  - disadvantage 1 pwm driver acceptable for CaDa motor, so combined but smaller controller is better
  


# Power & Sense Management 

## Sensors

### LiDAR

### Cameras

### Gyro


## Power Management

### Power Consumption Check

### Power Supply

### Power Distribution

### Wiring Diagram

We created the wiring diagram using the Fritzing software package.
Unfortunately, there was no Fritzing element for our Seengreat Motor and Servo Driver HAT. 
So we looked up the elements and their internal wiring in the manufacturer's docs and included these elements separately in our wiring diagram.
We then drew a blue rectangle to indicate which elements are indeed part of the Seengreat HAT.
These are a 5V-Step-Down, a TB1266FNG Motor driver, a PCA9685 PWM Driver and an on/off switch.

<div align="center">
  <img src="./schemes/Wiring_Diagram_2026.png">
</div>

Even though the connections to the Raspberry Pi can be seen in the wiring diagram, we also added this graphic to show which cable color for which purpose goes to the Raspberry Pi headers.
If a cable comes loose, this graphic helps to put it back in place easily.

<div align="center">
  <img src="./schemes/Raspi_pinout_connections.png">
</div>


# Software Architecture & Obstacle Strategy 



# Debugging & Testing 




# Overall System & Engineering Decisions

## Development Goals

## Design Trade-Offs

- LiDAR vs ToF Sensors
- LiDAR and Chassis height
- chassis height (wheel size) and speed
- speed and rear axle gearing
- motor choice: speed, gearing and pwm frequency stability
- previous car: separate motor controller and servo controller.
- this year: goal: use combined controller to save space and build flat enough for LiDAR
- test 3 types: adeept robot hat 3.0, waveshare robot driver hat and Seengreat motor and servo hat.
- problem: only 1 pca9685 pwm driver for both motor pwm and servo pwm.
  - servo: needs 50 Hz pwm frequency, motors: typically uses a lot higher frequency -> not possible with only 1 pwm driver
  - original lego PFL Motor rattles loudly at low speed and 50 Hz, CaDa rattles much less due to better gearing quality
  - disadvantage 1 pwm driver acceptable for CaDa motor, so combined but smaller controller is better

- LiDAR and Camera position
- LiDAR, python GIL and software design


# Appendices

## Hardware Bill of Materials

## Software Modules

- Raspbian Bookworm Operating System
- OpenCV image processing
- Adafruit Blinka (Interface to circuitpython/micropython libs for electronic hardware modules)
- Adafruit_CircuitPython_BNO08x
- Adafruit-PCA9685
- GitHub: nannigalaxy/ldrobot_lidar

## Resources




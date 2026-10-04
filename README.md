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
    - [Motorization](#motorization)
    - [Steering Mechanism](#Steering-Mechanism)
	- [Driving Base](#driving-base)
	- [Controllers](#controllers)
- [Power & Sense Management](#Power--Sense-Management)  
    - [Sensors](#Sensors)
		- [LiDAR](#lidar)
		- [Cameras](#cameras)
		- [Gyro](#gyro)
	- [Power Management](#Power-management)
		- [Power Consumption Check](#power-consumption-check)
		- [Power Supply](#power-supply)
		- [Power Distribution](#power-distribution)
		- [Wiring Diagram](#wiring-diagram)
- [Software Architecture & Obstacle Management](#software-architecture--obstacle-management)
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

A major point in improvements was to use a LiDAR for sensing distances and mount it in a way that it has a free 360 degree field of view. We felt this would be helpful in solving various previous weaknesses during driving and parking. However, this goal had major implications on how to build the chassis and which electronics can be used. A detailed discussions is provided in the sections about chassis and LiDAR sensor.

We sum up all the design trade-offs and the reasons for the final decisions in detail in the section [**Overall System & Engineering Decisions**](#overall-system--engineering-decisions).

Apart from specific goals for this season, we have defined some general engineering rules for ourselves.

- precision before speed
A better precision makes it more likely to run without driving errors. So it ranks higher than running at higher speed.

- test new ideas early 
Test early wether a new idea is helpful with prototypes. Find drawbacks as early as possible.

- Always have a backup


# Overview

<div align="center">
  <img src="./v-photos/rr_beauty02.png" width="50%">
</div>

## Roadrunner Fact Sheet

| Property                  | Value                                                        |
| ------------------------- | ------------------------------------------------------------ |
| Height                    | 9,5 cm                                                       |
| Width                     | 13,5 cm                                                      |
| Length                    | 18,8 cm                                                      |
| Weight                    | 572 g                                                        |
| Speed Range               | min: 0.13 m/sec  max: 1.58 m/sec                             |
| Overall power consumption | 16.2 W                                                       |
| Chassis build system      | Lego Technic  (mostly)                                       |
| Motorization              | lego-compatible motor driving rear axle, 1:1 gearbox connection, no encoder |
| Steering system           | Ackermann front  steering with differential rear axle        |
| Sensing system            | 2 RPI cams, 360 degree LiDAR, IMU (Gyro+Acceleration)        |
| Controller                | Raspberry Pi5 8 GB + Motor and Servo HAT                     |
| Programming               | Python                                                       |



## Car Photos
Here is an overview of our final car design. High-resolution photos can be found [**in v-photos**](./v-photos/README.md). 
<table> <tr> <td align="center">
    <img src="./v-photos/front_labels.png" width="90%"><br>Front View</td> <td align="center">
        <img src="./v-photos/back_labels.png" width="90%"><br>Back View</td> </tr> <tr> <td align="center">
            <img src="./v-photos/top_labels.png" width="90%"><br>Top View</td> <td align="center">
                <img src="./v-photos/bottom_labels.png" width="90%"><br>Bottom View</td> </tr> <tr> <td align="center">
                    <img src="./v-photos/right_labels.png" width="90%"><br>Right Side</td> <td align="center">
                        <img src="./v-photos/left_labels.png" width="90%"><br>Left Side</td> </tr> </table>




# Mobility & Mechanical Design 


Our previous roadrunner car has been build from lego technic parts and we decided to keep it that way. Lego Technic is a rather sturdy material and we have lots of technic parts from other lego robotic projects in the past. 

The alternative would have been to build the chassis in 3D-printing. However, rapid prototyping, testing new ideas, new placements, other gearings etc is faster with already pre-produced parts and later changes, e.g. for surprise rules,  are easier to be applied to a lego chassis.

To be able to use a LiDAR with 360 degree FoV  (goal for this season, see above), 

- the LiDAR must be mounted so its sensor's plane of rotation is significantly below 10 cm wall and obstacles height

- all other chassis and electronics elements must be placed below the LiDAR sensor's plane of rotation.

Detailed building instructions for the resulting chassis and the bill of materials can be found in [**Building_Instructions**](./Building_Instructions/README.md).

## Motorization

## Steering Mechanism

## Driving Base

## Controllers

- previous car: separate motor controller ans servo controller.
- this year: goal: use combined controller to save space and buils flat enough for LiDAR
- test 3 types: adeept robot hat 3.0, waveshare robot driver hat and seengrat motor and servo hat.
- problem: only 1 pca9685 pwm driver for both motor pwm and servo pwm.
  servo: needs 50 Hz pwm frequency, motors: typically uses a lot higher frequency -> not possible with only 1 pwm driver
  original lego PFL Motor rattles loudly at low speed and 50 Hz, CaDa rattles much less due to better gearing quality
  disadvantage 1 pwm driver acceptable for CaDa motor, so combined but smaller controller is better
  


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
- previous car: separate motor controller ans servo controller.
- this year: goal: use combined controller to save space and buils flat enough for LiDAR
- test 3 types: adeept robot hat 3.0, waveshare robot driver hat and seengrat motor and servo hat.
- problem: only 1 pca9685 pwm driver for both motor pwm and servo pwm.
  servo: needs 50 Hz pwm frequency, motors: typically uses a lot higher frequency -> not possible with only 1 pwm driver
  original lego PFL Motor rattles loudly at low speed and 50 Hz, CaDa rattles much less due to better gearing quality
  disadvantage 1 pwm driver acceptable for CaDa motor, so combined but smaller controller is better

- LiDAR and Camera position
- LiDAR, python GIL and software design


# Appendices

## Hardware Bill of Materials

## Software Modules

- Rasbian Bookworm Operating System
- OpenCV image processing
- Adafruit Blinka (Interface to circuitpython/micropython libs for electronic hardware modules)
- Adafruit_CircuitPython_BNO08x
- Adafruit-PCA9685
- GitHub: nannigalaxy/ldrobot_lidar

## Resources




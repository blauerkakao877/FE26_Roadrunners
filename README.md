Roadrunners – Future Engineers 2026
====
<div align="center">
  <img src="./other/Roadrunners_log_groß_trans.jpeg" width="60%" alt="Roadrunners Logo">
</div>

## Table of Contents

- [Introduction](#introduction)
- [Overview](#overview)
	- [Roadrunner Fact Sheet](#roadrunner-fact-sheet)
	- [Car Photos](#car-photos)
- [Mobility & Mechanical Design](#mobility--mechanical-design)
    - [Motorization](#motorization)
    - [Steering Mechanism](#Steering-Mechanism)
	- [Chassis](#Chassis)
		- [Driving Base](#driving-base)
		- [Wheels](#wheels)
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

Welcome to the GitHub hub of **Team Roadrunners**, proudly representing **Germany⚫🔴🟡** at the **WRO Worldfinal 2026**!

This repository contains all the code, documentation, and resources for our project. We have used scoring criteria from the rulebook as headings in our documentation to make it easy to navigate through our repository.

# Overview

<div align="center">
  <img src="./v-photos/rr_beauty02.png" width="50%">
</div>

## Roadrunner Fact Sheet

| Measurement | Value      |
| ----------- | ---------- |
| Height      | 9,5 cm     |
| Width       | 13,5 cm    |
| Length      | 18,8 cm    |
| Weight      | 572 g      |
| min. Speed  | 0.13 m/sec |
| max. Speed  | 1.58 m/sec |



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

## Motorization

## Steering Mechanism

## Chassis

Detailed building instructions for the chassis can be found [**in Building_Instructions**](./Building_Instructions/README.md).

### Driving Base

### Wheels

### Controllers


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



# Appendices

## Hardware Bill of Materials

## Software Modules

## Resources




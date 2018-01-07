#!/bin/bash

cd ~/homework_checker/Khan-Academy-Homework-Checker

export AWS_PROFILE=DanielEvansNonRoot

source ../bin/activate

python homeworkchecker.py

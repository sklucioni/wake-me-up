import time
import pygame
import pygame, sys
from pygame.locals import *
import subprocess
import RPi.GPIO as GPIO
from time import sleep

pygame.init()

infoObject = pygame.display.Info()

#song list
songs = ['alarm1', 'alarm2', 'alarm3','alarm4','alarm5',]
song_loc = '/home/pi/Desktop/oeop_code/'
pygame.mixer.init()

current_song = 0 #used to count through songs!

#preload a song, play it, immediately pause it!
#pygame.mixer.music.load(song_loc+songs[current_song]+'.mp3')
#pygame.mixer.music.play()
#pygame.mixer.music.pause()

#drive pattern list
patterns = ['back and forth', 'bump and back', 'back and turn']
current_pattern = 0

############################################### code for the buttons
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#set up pins
inputs = [19,4,5,6,13,26] #numUp, switchSlot, alarmOff, changeSound, drivePattern, frontClicker
for x in inputs:
    GPIO.setup(x,GPIO.IN,pull_up_down=GPIO.PUD_UP)

switch_state = [True,True,True,True,True,True]

#initialize switch state values!
for x in range(len(inputs)):
    #print(inputs[x])
    switch_state[x] = GPIO.input(inputs[x])
#######################################

####################################### Motor setup
MotorA = 18
MotorB = 24
MotorC = 25
MotorD = 12

GPIO.setup(MotorA,GPIO.OUT)
GPIO.setup(MotorB,GPIO.OUT)
GPIO.setup(MotorC,GPIO.OUT)
GPIO.setup(MotorD,GPIO.OUT)

pwmA=GPIO.PWM(MotorA,800)
pwmA.start(0)
pwmB=GPIO.PWM(MotorB,800)
pwmB.start(0)
pwmC=GPIO.PWM(MotorC,800)
pwmC.start(0)
pwmD=GPIO.PWM(MotorD,800)
pwmD.start(0)
#######################################
#global variables

SCREENWIDTH = infoObject.current_w
SCREENHEIGHT = infoObject.current_h

FPS = 30 # frames per second setting
fpsClock = pygame.time.Clock()

DISPLAYSURF = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))

gentiumFont = (pygame.font.SysFont('roboto', 50))
gentiumFont2 = (pygame.font.SysFont('roboto', 30))
gentiumFont3 = (pygame.font.SysFont('roboto', 20))

#['robotocondensed', 'dejavuserif', 'dejavusansmono', 'freemono', 'gentiumbasic', 'freesans', 'opensymbol', 'dejavusans', 'gentiumbookbasic', 'freeserif', 'roboto']
BASICFONT = pygame.font.Font('freesansbold.ttf', 20)
TITLEFONT = pygame.font.Font('freesansbold.ttf', 75)
MIDFONT = pygame.font.Font('freesansbold.ttf', 35)
INSFONT = pygame.font.Font('freesansbold.ttf', 12)

#make some colors with easy to understand names for use throughout game:
WHITE = (255,255,255)
GREY = (200, 200, 200)
RED = (255,0,0)
GREEN = (67,104,55)
BLUE = (0,0,255)
LIGHTBLUE = (144,195,212)
LIGHTPURPLE = (146,121,183)
PURPLE = (147,49,196)
ORANGE = (249,246,29)
PINK = (255,192,203)
YELLOW = (255,255,0)
BLACK = (0,0,0)

#important variables
alarmState = "ON"
alarmTime = "06:00:00 AM"
switchNum = 0
#numUp, switchSlot, alarmOff, changeSound, drivePattern
click = 0
count = 0
turnCount = 0
alarmON = False

def main():
    global alarmState, CLOCK, switchNum, click, current_pattern
    pygame.init()
    CLOCK = pygame.time.Clock()
    pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    display()
    while True :
        display()
        alarm(1)
        pygame.display.update()
        fpsClock.tick(FPS)
        #if stopAlarm button is pressed or changeTime button (== False) then call setAlarm
        #setAlarm(button)

        #########################Check button values
        values = []
        for x in inputs:
            values.append(GPIO.input(x))
        output = readInputs(values)
##      if output != None:
##          print(output)
        if output == 'numUp':
            setAlarm('numUp')
        elif output == 'switchSlot':
            switchNum+=1
            if switchNum == 3:
                switchNum = 0
        elif output == 'off':
            alarm(0)
            if alarmState == "ON":
                alarmState = "OFF"
            else:
                alarmState = "ON"
        elif output == 'changeSound':
            changeSound()
        elif output == 'changePattern':
            current_pattern += 1
            if current_pattern == 3:
                current_pattern = 0
        elif output == 'frontClicked':
            click +=1
            move(click)
        #########################
        
        for event in pygame.event.get():
            if event.type == QUIT:
                GPIO.cleanup()
                terminate()

def display():
    DISPLAYSURF.fill(LIGHTBLUE)
    #Name
    name = gentiumFont.render('Wake Me Up', True, WHITE)
    DISPLAYSURF.blit(name, (30, 20))
    name = gentiumFont2.render('Alarm Clock', True, WHITE)
    DISPLAYSURF.blit(name, (30, 70))
    #show time
    TitleSurf = TITLEFONT.render(getTime(), True, BLACK)
    DISPLAYSURF.blit(TitleSurf, (195, 140))
    #show alarmTime and alarm on/off
    alarmTTime = MIDFONT.render(alarmTime+" "+alarmState, True, RED)
    DISPLAYSURF.blit(alarmTTime, (280, 230))
    #show song choice
    alarmS = gentiumFont2.render("Alarm is set to: "+songs[current_song], True, PURPLE)
    DISPLAYSURF.blit(alarmS, (270, 300))
    #show drive pattern
    pp = gentiumFont2.render("Drive Pattern is set to: "+patterns[current_pattern], True, BLACK)
    DISPLAYSURF.blit(pp, (180, 335))

    #Unnecessary text
    button1 = BASICFONT.render("Num Up", True, GREEN)
    DISPLAYSURF.blit(button1, (10, 390))
    button2 = BASICFONT.render("H:M:AM/PM", True, YELLOW)
    DISPLAYSURF.blit(button2, (110, 390))
    button3 = BASICFONT.render("On/Off", True, RED)
    DISPLAYSURF.blit(button3, (250, 390))
    button4 = BASICFONT.render("Alarm Sound", True, BLUE)
    DISPLAYSURF.blit(button4, (340, 390))
    button4 = BASICFONT.render("Drive Pattern", True, WHITE)
    DISPLAYSURF.blit(button4, (480, 390))
    #numUp, switchSlot, alarmOff, changeSound, drivePattern
    button5 = gentiumFont3.render("Rafid is the worst TA", True, WHITE)
    DISPLAYSURF.blit(button5, (600, 420))

def getTime():
    return (time.strftime("%I:%M:%S %p", time.localtime(time.time())))

def setAlarm(button):
    global alarmTime
    global switchNum
    #hours
    if button == 'numUp':
        if switchNum == 0:
            num = int(alarmTime[0:2])
            num+=1
            if num <10:
                alarmTime = '0'+str(num)+alarmTime[2:]
            elif num <13:
                alarmTime = str(num)+alarmTime[2:]
            else:
                num = num - 12
                alarmTime = '0'+str(num)+alarmTime[2:]
        #minutes
        elif switchNum == 1:
            num = int(alarmTime[3:5])
            num+=1
            if num <10:
                alarmTime = alarmTime[0:3]+'0'+str(num)+alarmTime[5:]
            elif num <60:
                alarmTime = alarmTime[0:3]+str(num)+alarmTime[5:]
            else:
                num = num - 60
                alarmTime = alarmTime[0:3]+'0'+str(num)+alarmTime[5:]
        #AM PM
        elif switchNum == 2:
            AMPM = alarmTime[9:]
            if AMPM == 'AM':
                alarmTime = alarmTime[0:9]+'PM'
            else:
                alarmTime = alarmTime[0:9]+'AM'
        pygame.display.update()

def changeSound():
    global current_song, songs
    if current_song < len(songs)-1:
        current_song+=1
    else:
        current_song = 0
    pygame.display.update()

def alarm(onOff):
    global current_song
    global alarmTime
    global click
    global count
    global alarmON
    if alarmState == "ON":
        if alarmTime == getTime():
            pygame.mixer.music.load(song_loc+songs[current_song]+'.mp3')
            pygame.mixer.music.play()
            move(click)
            alarmON = True
        if alarmON == True and alarmState == "ON":
            move(click)
        if onOff == 0:
            stopMove()
            click = 0
            count = 0
            alarmON = False
            pygame.mixer.music.stop()
    
def move(num):
    global current_pattern
    #get pattern (1 of a list of 3)
    if current_pattern == 0:
        backNForth() #1
    elif current_pattern == 1:
        bumpNBack(num) #2
    elif current_pattern == 2:
        bumpNTurn(num) #3
    #rip square pattern

def backNForth(): #renee's fault
    global turnCount
    if alarmON:
        if turnCount<75:
            forward()
            turnCount+=1
        elif turnCount < 150:
            backward()
            turnCount+=1
        elif turnCount >= 150:
            turnCount = 0

def bumpNBack(x):
    global alarmON
    if alarmON:
        if x%2 == 0:
            forward()
        else:
            backward()

def bumpNTurn(x):
    global count, turnCount, alarmON
    if alarmON == True:
        if x == count:
            forward()
        else:
            if turnCount<50:
                backward()
                turnCount+=1
                print(turnCount)
            elif turnCount < 100:
                leftTurn()
                turnCount+=1
                print(turnCount)
            else:
                turnCount = 0
                count+=1
    

def forward():
    stopMove()
    pwmA.ChangeDutyCycle(80)
    pwmD.ChangeDutyCycle(80)

def backward():
    stopMove()
    pwmB.ChangeDutyCycle(80)
    pwmC.ChangeDutyCycle(80)

def leftTurn():
    stopMove()
    pwmB.ChangeDutyCycle(90)
    pwmD.ChangeDutyCycle(90)

def rightTurn():
    stopMove()
    pwmA.ChangeDutyCycle(80)
    pwmC.ChangeDutyCycle(80)

def stopMove():
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)
    pwmC.ChangeDutyCycle(0)
    pwmD.ChangeDutyCycle(0)

def readInputs(readings):
    global switch_state 
    newList= []
    for x in range(len(readings)):
        if readings[x] == switch_state[x]: #nothing changed
            newList.append(False)
        elif switch_state[x] == True and readings[x] == False: #button pressed
            newList.append(True)
        else:
            newList.append(False)
    switch_state = readings
    if newList[0] == True:
        return "numUp"
    elif newList[1] == True:
        return "switchSlot"
    elif newList[2] == True:
        return "off"
    elif newList[3] == True:
        return "changeSound"
    elif newList[4] == True:
        return "changePattern"
    elif newList[5] == True:
        return "frontClicked"

def terminate():
    pygame.quit()
    sys.exit()


#code below runs the main function when you just call python3 lab08.py in terminal
if __name__ == '__main__':
    main()

try:
    while True:
        main()
except KeyboardInterrupt:
    GPIO.cleanup()
    terminate()
    

# -*- coding: utf-8 -*-

#Python 3.5.x

import os
import sys
import datetime

import math
import random


__metaclass__ = type


class Maze():
    #迷宫类
    
    #用一个二维数组代表迷宫
    #N = Empty
    #W = Wall
    #S = Starting Position
    #R = Route
    #E = Goal Position
    
    #X代表水平方向
    #Y代表竖直方向
    
    maze=[[]]
    startPosition=[-1,-1]
    
    
    def __init__(self, maze):
        #初始化一个迷宫
        self.maze=maze
    
    def getStartPosition(self):
        #返回迷宫的入口
        if self.startPosition[0] != -1 and self.startPosition[1] != -1:
            return self.startPosition
        
        #返回默认的值
        self.startPosition=[0,0]
        for rowIndex in range(len(self.maze)):
            for colIndex in range(len(self.maze[rowIndex])):
                if self.maze[rowIndex][colIndex]=='S':
                    self.startPosition=[colIndex, rowIndex]
        return self.startPosition
    
    def getPositionValue(self, x, y):
        #返回迷宫中某个点的值
        return self.maze[y][x]

    def isWall(self, x, y):
        #判断某一点是否是墙
        if 0<=x<=self.getMaxX() and 0<=y<=self.getMaxY():
            return self.getPositionValue(x, y)=='W'
        else:
            return True
    
    def getMaxX(self):
        #获取水平X方向最大取值范围
        return len(self.maze[0])-1
    
    def getMaxY(self):
        #获取竖直Y方向最大取值范围
        return len(self.maze)-1
    
    def scoreRoute(self, route):
        #评估机器人踩到正确地砖的次数
        #route是一个由经过的地砖位置组成的数组
        
        score=0
        visited=[[False for col in range(self.getMaxX()+1)] for row in range(self.getMaxY()+1)]

        for routeStep in route:
            stepX=routeStep[0]
            stepY=routeStep[1]
            
            if self.maze[stepY][stepX]=='R' and visited[stepY][stepX] == False:
                #走到了未曾走过的可踩地砖，增加一个积分
                score+=1
                #将这个位置设置为已经踩过
                visited[stepY][stepX]=True
        return score
    
    def flatten(self, nested):
        try:
            for sublist in nested:
                if sublist==nested:
                    raise TypeError
                for element in self.flatten(sublist):
                    yield element
        except TypeError:
            yield nested
    
    def calcMaxFitness(self):
        #计算一个迷宫的最大适应度，即最长路由是多少
        #这不是一个

        return len([item for item in self.flatten(self.maze) if item == 'R'])   
    
class Robot():
    xPosition=0
    yPosition=0
    
    heading=None
    
    maxMoves=0
    moves=0
    sensorVal=0
    sensorActions=[]
    maze=None
    route=[]
    
    def __init__(self, sensorActions, maze, maxMoves):
        self.sensorActions=self.calcSensorActions(sensorActions)
        self.maze=maze
        startPos=self.maze.getStartPosition()
        self.xPosition=startPos[0]
        self.yPosition=startPos[1]
        self.sensorVal=-1
        self.heading="North"
        self.maxMoves=maxMoves
        self.moves=0
        self.route=[]
        self.route.append(startPos)
    
    def run(self):
        #运行一个机器人
        while True:
            self.moves+=1
            
            #如果机器人停止运行就返回
            if self.getNextAction()=="N":
                return
            
            #如果到达出口就返回
            if self.maze.getPositionValue(self.xPosition, self.yPosition) == 'E':
                return
            
            #如果机器人的步数超过限定值，就返回
            if self.moves>self.maxMoves:
                return
            
            #执行动作
            self.makeNextAction()
            
    def calcSensorActions(self, sensorActionsStr):
        #映射一个机器人传感器数据到动作
        #@param sensorActionsStr:二进制的遗传染色体
        #@return 将传感器数据映射到动作的数组
        
        #有多少种动作？
        numActions=int(len(sensorActionsStr)/2)
        sensorActions=[]
        
        #每种传感器组合进行遍历
        for sensorValue in range(numActions):
            #获取传感器动作
            sensorAction=0
            
            if sensorActionsStr[sensorValue*2]==1:
                sensorAction+=2
            
            if sensorActionsStr[sensorValue*2+1]==1:
                sensorAction+=1
            
            #添加到 "传感器-动作" 映射表 
            sensorActions.append(["N", "L", "R", "F"][sensorAction])
        
        return sensorActions
    
    def makeNextAction(self):
        #执行下一动作
        nextAction=self.getNextAction()
        
        #如果是向前进
        if nextAction=="F":
            currentX=self.xPosition
            currentY=self.yPosition
            #前进动作依赖于当前的方向
            if self.getHeading() == "North":
                self.yPosition-=1
                self.yPosition=max(self.yPosition, 0)
            elif self.getHeading() == "East":
                self.xPosition+=1
                self.xPosition=min(self.xPosition, self.maze.getMaxX())
            elif self.getHeading() == "South":
                self.yPosition+=1
                self.yPosition=min(self.yPosition, self.maze.getMaxY())
            elif self.getHeading() == "West":
                self.xPosition-=1
                self.xPosition=max(self.xPosition, 0)  
            else:
                assert 0
            #我们不能到的地方
            if self.maze.isWall(self.xPosition, self.yPosition):
                self.xPosition=currentX
                self.yPosition=currentY
            else:
                if self.xPosition!=currentX or self.yPosition!=currentY:
                    self.route.append(self.getPosition())
        #如果顺时针转动
        elif nextAction=="R":
            if self.getHeading() == "North":
                self.heading = "East"
            elif self.getHeading() == "East":
                self.heading = "South"
            elif self.getHeading() == "South":
                self.heading = "West"                
            elif self.getHeading() == "West":
                self.heading = "North"
            else:
                assert 0
        #如果逆时针转动
        elif nextAction=="L":
            if self.getHeading() == "North":
                self.heading = "West"
            elif self.getHeading() == "West":
                self.heading = "South"
            elif self.getHeading() == "South":
                self.heading = "East"                
            elif self.getHeading() == "East":
                self.heading = "North"
            else:
                assert 0
        #清除传感器值
        self.sensorVal=-1
    
    def getNextAction(self):
        #根据"传感器-动作"映射表得出下一步动作
        return self.sensorActions[self.getSensorValue()]
    
    def getSensorValue(self):
        #获取传感器值
        
        #如果已经获取过传感器数据就直接返回
        if self.sensorVal != -1:
            return self.sensorVal
        
        frontSensor=frontLeftSensor=frontRightSensor=leftSensor=rightSensor=backSensor=False
        #找出哪些传感器是被激活的
        if self.getHeading() == "North":
            frontSensor=self.maze.isWall(self.xPosition, self.yPosition-1)
            frontLeftSensor=self.maze.isWall(self.xPosition-1, self.yPosition-1)
            frontRightSensor=self.maze.isWall(self.xPosition+1, self.yPosition-1)
            leftSensor=self.maze.isWall(self.xPosition-1, self.yPosition)
            rightSensor=self.maze.isWall(self.xPosition+1, self.yPosition)
            backSensor=self.maze.isWall(self.xPosition, self.yPosition+1)
        elif self.getHeading() == "East":
            frontSensor=self.maze.isWall(self.xPosition+1, self.yPosition)
            frontLeftSensor=self.maze.isWall(self.xPosition+1, self.yPosition-1)
            frontRightSensor=self.maze.isWall(self.xPosition+1, self.yPosition+1)
            leftSensor=self.maze.isWall(self.xPosition, self.yPosition-1)
            rightSensor=self.maze.isWall(self.xPosition, self.yPosition+1)
            backSensor=self.maze.isWall(self.xPosition-1, self.yPosition)
        elif self.getHeading() == "South":
            frontSensor=self.maze.isWall(self.xPosition, self.yPosition+1)
            frontLeftSensor=self.maze.isWall(self.xPosition+1, self.yPosition+1)
            frontRightSensor=self.maze.isWall(self.xPosition-1, self.yPosition+1)
            leftSensor=self.maze.isWall(self.xPosition+1, self.yPosition)
            rightSensor=self.maze.isWall(self.xPosition-1, self.yPosition)
            backSensor=self.maze.isWall(self.xPosition, self.yPosition-1)
        elif self.getHeading() == "West":
            frontSensor=self.maze.isWall(self.xPosition-1, self.yPosition)
            frontLeftSensor=self.maze.isWall(self.xPosition-1, self.yPosition+1)
            frontRightSensor=self.maze.isWall(self.xPosition-1, self.yPosition-1)
            leftSensor=self.maze.isWall(self.xPosition, self.yPosition+1)
            rightSensor=self.maze.isWall(self.xPosition, self.yPosition-1)
            backSensor=self.maze.isWall(self.xPosition+1, self.yPosition)
        else:
            assert 0
            
        #计算传感器二进制值
        sensorVal=0
        sensorVal+=(1 if frontSensor else 0)
        sensorVal+=(2 if frontLeftSensor else 0)
        sensorVal+=(4 if frontRightSensor else 0)
        sensorVal+=(8 if leftSensor else 0)
        sensorVal+=(16 if rightSensor else 0)
        sensorVal+=(32 if backSensor else 0)
        
        self.sensorVal=sensorVal
        
        return sensorVal
    
    def getPosition(self):
        #获得机器人的当前位置
        return [self.xPosition, self.yPosition]
    
    def getHeading(self):
        #获取机器人的方向
        
        return self.heading
    
    def getRoute(self):
        #返回机器人的完整路由
        
        return self.route
    
    def printRoute(self):
        #返回可打印的路由字符串
        route=""
        
        for routeStep in self.route:
            route+="{"+str(routeStep[0])+","+str(routeStep[1])+"}"
        return route
                
                
class Individual():
    #专注于个体自身行为的类
    
    chromosome=[]       #染色体
    fitness=0.0         #适应度
    
    def __init__(self, chromosome=[], chromosomeLength=0):
        #初始化一个个体，使用传入的染色体，或者随机生成一个染色体长度是chromosomeLength的染色体
        if chromosome:
            self.chromosome=chromosome
        elif chromosomeLength>0:
            self.chromosome=[0]*chromosomeLength
            for i in range(chromosomeLength):
                if (0.5 < random.random()):
                    self.setGene(i, 1)
                else:
                    self.setGene(i, 0)
        else:
            assert 0,"Para Error"
        self.fitness=0.0
    
    def getChromosome(self):
        #取染色体
        return self.chromosome
    
    def getChromosomeLength(self):
        #取染色体长度
        return len(self.chromosome)
    
    def setGene(self, offset, gene):
        #设置具体一个基因
        self.chromosome[offset]=gene
    
    def getGene(self, offset):
        #取具体一个基因
        return self.chromosome[offset]
        
    def setFitness(self, fitness):
        #设置个体适应度
        self.fitness=fitness
    
    def getFitness(self):
        #取个体适应度
        return self.fitness
    
    def toString(self, type=0):
        #将染色体转为可打印字符串
        if type==0:
            outStr="".join([str(item) for item in self.chromosome])
        elif type==1:
            outStr=""
            for i in range(int(self.getChromosomeLength()/2)):
                Vec=''.join(["0"]*(6-len(bin(i)[2:])))+bin(i)[2:]
                Val=["N", "L", "R", "F"][self.getGene(i*2)*2+self.getGene(i*2+1)]
                outStr+="{"+Vec+":"+Val+"}"
        else:
            assert 0
        
        return outStr


class Population():
    #种群类，专注于个体在种群中行为的类
    population=[]           #Individual构成的种群
    populationFitness=0.0   #种群适应度
    
    def __init__(self, populationSize, chromosomeLength):
        #初始化一个populationSize数量个个体的，每个个体的染色体长chromosomeLength的种群
        self.population=[]
        self.populationFitness=0.0
        for i in range(populationSize):
            self.population.append(Individual(chromosomeLength=chromosomeLength))
            
    def getIndividuals(self):
        #返回种群
        return self.population
    
    def getFittest(self, offset):
        self.population.sort(key=lambda x:x.getFitness(), reverse=True)     #适应度最高的排前面
        return self.population[offset]
    
    def setPopulationFitness(self, fitness):
        self.populationFitness = fitness
        
    def getPopulationFitness(self):
        return self.populationFitness
    
    def size(self):
        #取种群数量
        return len(self.population)
    
    def setIndividual(self, offset, individual):
        #设置一个个体
        self.population[offset]=individual
    
    def getIndividual(self, offset):
        #取一个个体
        return self.population[offset]
        
    def shuffle(self):
        #将种群中个体进行打乱顺序
        random.shuffle(self.population)


class GeneticAlgorithm():
    populationSize=0        #种群规模
    mutationRate=0.0        #变异率
    crossoverRate=0.0       #交叉率
    elitismCount=0          #精英成员数
    
    tournamentSize=0        #锦标赛规模
    
    def __init__(self, populationSize, mutationRate, crossoverRate, elitismCount, tournamentSize):
        self.populationSize=populationSize
        self.mutationRate=mutationRate
        self.crossoverRate=crossoverRate
        self.elitismCount=elitismCount
        self.tournamentSize=tournamentSize
        return
    
    def initPopulation(self, chromosomeLength):
        return Population(self.populationSize, chromosomeLength)    
    
    def calcFitness(self, individual, maze):
        #计算适应度
        #@param individual:个体， maze：迷宫地图
        #@return 个体对地图的适应度
        
        #获取个体的基因，也就是这个个体的“传感器-动作映射表”
        chromosome = individual.getChromosome()   
        
        #基于这个个体的基因构造一个机器人
        robot = Robot(chromosome, maze, 100)
        
        #运行机器人，让其在迷宫中走一下
        robot.run()
        
        #适应度就是这个机器人在迷宫中走的有效步数
        fitness = maze.scoreRoute(robot.getRoute())
        
        #保存个体的适应度评估结果
        individual.setFitness(fitness)
        
        return fitness

    def evalPopulation(self, population, maze):
        #评估一个群体对迷宫的表现
        #@param population:群体， maze：迷宫地图
        #@return None
        
        populationFitness=0
        
        #遍历所有个体，计算每个个体的适应度，加合得到群体适应度
        for individual in population.getIndividuals():
            populationFitness += self.calcFitness(individual, maze)
        
        #保存群体适应度
        population.setPopulationFitness(populationFitness)
        
    def isTerminationConditionMet(self, generationsCount, maxGenerations, fittestIndividual, maze):
        #是否达到终止进化的条件
        #@param generationsCount:当前进化代数， maxGenerations:最大允许代数, fittestIndividual:群体中的最优个体, maze:迷宫
        #@return True or False

        if self.calcFitness(fittestIndividual, maze)==maze.calcMaxFitness() or generationsCount>maxGenerations:
            return True

        return False
    
    def selectParent(self, population):
        #选择亲代，这里使用锦标赛的方式
        #@param population:亲代群体
        #@return 锦标赛胜出的亲代个体
        
        #创建锦标赛
        tournament = Population(self.tournamentSize, population.getIndividual(0).getChromosomeLength())
        
        #随机洗牌，取出参加锦标赛的子群
        population.shuffle()
        for i in range(self.tournamentSize):
            tournament.setIndividual(i, population.getIndividual(i))
        
        #返回锦标赛中最好的亲代
        return tournament.getFittest(0)
    
    def crossoverPopulation(self, population):
        #染色体交叉
        #@param population:亲代群体
        #@return 
        
        #创建新群体
        newPopulation = Population(population.size(), population.getIndividual(0).getChromosomeLength())
        
        for populationIndex in range(population.size()):
            #取出适应度排在populationIndex顺位的个体
            parent1 = population.getFittest(populationIndex)
            
            #如果概率要求交叉，并且不是精英
            if self.crossoverRate > random.random() and populationIndex >= self.elitismCount:
                #初始化一个子代
                offspring = Individual(chromosomeLength=parent1.getChromosomeLength())
                
                #通过锦标赛方式找到另一个亲代
                parent2 = self.selectParent(population)
                
                #得到随机交叉点
                swapPoint = random.random()*(parent1.getChromosomeLength()+1)
                
                #遍历基因组
                for geneIndex in range(parent1.getChromosomeLength()):
                    if geneIndex<swapPoint:
                        offspring.setGene(geneIndex, parent1.getGene(geneIndex))
                    else:
                        offspring.setGene(geneIndex, parent2.getGene(geneIndex))
                
                #将子代加入新群体
                newPopulation.setIndividual(populationIndex, offspring)
            else:#不需要与其他个体交叉基因
                newPopulation.setIndividual(populationIndex, parent1)
        
        return newPopulation

    def mutatePopulation(self, population):
        #种群基因突变
        
        #先构造一个新种群
        newPopulation=Population(population.size(), population.getIndividual(0).getChromosomeLength())
        
        #依适应度遍历种群
        for populationIndex in range(population.size()):
            individual=population.getFittest(populationIndex)
            #遍历这个个体的基因
            for geneIndex in range(individual.getChromosomeLength()):
                #忽略这个个体如果它是一个精英
                if populationIndex >= self.elitismCount:
                    
                    if (self.mutationRate > random.random()):
                        #需要变异
                        newGene=1
                        if individual.getGene(geneIndex)==1:
                            newGene=0
                        individual.setGene(geneIndex, newGene)
            
            #将变异后的个体加入新种群
            newPopulation.setIndividual(populationIndex, individual)
        return newPopulation
    
    
class RobotController():
    maxGenerations=1000
    
    def main(self):
        #N = Empty
        #W = Wall
        #S = Starting Position
        #R = Route
        #E = Goal Position
        
        #先初始化一个迷宫
        maze=Maze([\
            ['N', 'N', 'N', 'N', 'W', 'N', 'W', 'R', 'S'],\
            ['W', 'N', 'W', 'W', 'W', 'N', 'W', 'R', 'W'],\
            ['W', 'N', 'N', 'W', 'R', 'R', 'R', 'R', 'W'],\
            ['R', 'R', 'R', 'W', 'R', 'W', 'W', 'N', 'W'],\
            ['R', 'W', 'R', 'R', 'R', 'W', 'W', 'N', 'N'],\
            ['R', 'R', 'W', 'W', 'W', 'W', 'N', 'W', 'W'],\
            ['W', 'R', 'N', 'W', 'R', 'R', 'R', 'R', 'R'],\
            ['N', 'R', 'W', 'W', 'R', 'W', 'N', 'W', 'R'],\
            ['W', 'R', 'R', 'R', 'R', 'W', 'W', 'W', 'E'],\
        ])
        
        
        #创建算法对象
        #种群数量，变异率，交叉率，精英成员数
        ga=GeneticAlgorithm(200, 0.05, 0.9, 2, 10)
        
        #创建种群
        #基因长度128bit(6个传感器产生64个组合，每个组合有2bit代表4种动作)
        population = ga.initPopulation(128)
        
        #评估种群的适应度
        ga.evalPopulation(population, maze)
        
        generation=1        #第几代
        
        #开始进化循环
        while ga.isTerminationConditionMet(generation, self.maxGenerations, population.getFittest(0), maze)==False:
            #打印种群中适应度最好的个体
            fittest = population.getFittest(0)
            print ("G",generation," Best solution(", fittest.getFitness(),"): ",fittest.toString())
            print (fittest.toString(1))
            
            
            #交叉
            population = ga.crossoverPopulation(population)
            
            #突变
            population = ga.mutatePopulation(population)
            
            #评估种群
            ga.evalPopulation(population, maze)
            
            #代数增加
            generation+=1
        
        #打印结果
        print ("Found solution in %d generations" % generation)
        fittest=population.getFittest(0)
        print ("Best solution: "+ fittest.toString())
        print ("Best solution: "+ fittest.toString(1))
        print ("Best fitness: ",fittest.getFitness())
        
print ("00-None, 01-LEFT, 10-RIGHT, 11-FORWARD")
print ("back|right|left|frontRight|frontLeft|front")
        
entry=RobotController()
entry.main()


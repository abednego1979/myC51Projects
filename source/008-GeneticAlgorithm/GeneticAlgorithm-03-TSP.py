# -*- coding: utf-8 -*-

#Python 3.5.x

import os
import sys
import datetime

import math
import random


__metaclass__ = type


class City():    
    def __init__(self, x, y):
        self.x=x
        self.y=y
        
    def distanceFrom(self, city):
        deltaXSq = pow((city.getX()-self.getX()), 2)
        deltaYSq = pow((city.getY()-self.getY()), 2)
        distance = math.sqrt(deltaXSq+deltaYSq)
        return distance
    
    def getX(self):
        return self.x
    def getY(self):
        return self.y
    
class Route():
    
    def __init__(self, individual, cities):
        chromosome = individual.getChromosome()     #获取基因，其实就是按顺序到达的城市的编号
        #得到依次到达的城市编号的数组
        self.route = [cities[chromosome[geneIndex]] for geneIndex in range(len(chromosome))]
        
        self.distance=0.0
        
    def getDistance(self):
        #获取以一定路由遍历城市的总距离
        if self.distance:
            return self.distance
        
        totalDistance=0.0
        for cityIndex in range(len(self.route)-1):
            totalDistance+=self.route[cityIndex].distanceFrom(self.route[cityIndex+1])
        totalDistance+=self.route[len(self.route)-1].distanceFrom(self.route[0])
        self.distance=totalDistance
        return totalDistance
        
        
    
class Individual():
    #专注于个体自身行为的类
    
    chromosome=[]       #染色体
    fitness=0.0         #适应度
    
    def __init__(self, chromosome=[], chromosomeLength=0):
        #初始化一个个体，使用传入的染色体，或者生成一个染色体长度是chromosomeLength的染色体
        #基因就是依次到达的城市的编号。
        if chromosome:
            self.chromosome=chromosome
        elif chromosomeLength>0:
            self.chromosome=[gene for gene in range(chromosomeLength)]
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
    
    def toString(self):
        #将染色体转为可打印字符串
        
        outStr=''
        assert 0
        
        return outStr
    
    def containsGene(self, gene):
        if gene in self.chromosome:
            return True
        return False
        


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
    
    def calcFitness(self, individual, cities):
        #计算适应度
        #适应度就是个体走遍所有城市所途经距离的倒数
        
        fitness = 1/Route(individual, cities).getDistance()
        
        individual.setFitness(fitness)
        return fitness

    def evalPopulation(self, population, cities):
        #评估一个群体对某个城市组合的旅行适应度表现
        #@param
        #@return
        
        populationFitness=0
        
        #遍历群体，评估个体的适应度，并加合为群体适应度
        for individual in population.getIndividuals():
            populationFitness += self.calcFitness(individual, cities)
        
        #这里记录的是平均适应度，由于使用锦标赛而不是轮盘赌的方式，这个群体平均适应度其实没有什么用
        avgFitness = populationFitness/population.size()
        population.setPopulationFitness(avgFitness)

        return
        
    def isTerminationConditionMet(self, generationsCount, maxGenerations):
        #是否达到终止进化的条件
        #@param generationsCount:当前进化代数， maxGenerations:最大允许代数, fittestIndividual:群体中的最优个体, maze:迷宫
        #@return True or False

        if generationsCount>maxGenerations:
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
        #@param
        #@return
        
        #创建新群体
        newPopulation = Population(population.size(), population.getIndividual(0).getChromosomeLength())        
        
        #遍历种群
        for populationIndex in range(population.size()):
            #得到亲代1，即原种群中适应度排第populationIndex的个体
            parent1 = population.getFittest(populationIndex)
            
            #如果概率要求交叉，并且不是精英
            if self.crossoverRate > random.random() and populationIndex >= self.elitismCount:
                #通过锦标赛方式找到另一个亲代
                parent2 = self.selectParent(population)
                
                #创建一个空白的后代染色体
                offspring = Individual(chromosome=[-1]*parent1.getChromosomeLength())
                
                #获取亲代的染色体片段
                substrPos1=int(random.random()*parent1.getChromosomeLength())
                substrPos2=int(random.random()*parent1.getChromosomeLength())
                
                startSubstr=min(substrPos1, substrPos2)
                endSubstr=max(substrPos1, substrPos2)
                
                #把选中的亲代1的染色体片段复制给子代
                for i in range(startSubstr, endSubstr):
                    offspring.setGene(i, parent1.getGene(i))
                    
                #遍历亲代2，将亲代2的基因插入子代
                for i in range(parent2.getChromosomeLength()):
                    parent2Gene=(i+endSubstr)%parent2.getChromosomeLength()
                    
                    #如果子代没有包含当前指向的亲代2基因
                    if not offspring.containsGene(parent2.getGene(parent2Gene)):
                        #在子代中找一个空位保存这个来自亲代2的基因
                        for ii in range(offspring.getChromosomeLength()):
                            if offspring.getGene(ii)==-1:
                                offspring.setGene(ii, parent2.getGene(parent2Gene))
                                break
                
                newPopulation.setIndividual(populationIndex, offspring)
            else:#不需要与其他个体交叉基因
                newPopulation.setIndividual(populationIndex, parent1)

        return newPopulation

    def mutatePopulation(self, population):
        #种群基因突变
        
        #创建新群体
        newPopulation = Population(population.size(), population.getIndividual(0).getChromosomeLength())
        
        #依适应度遍历种群
        for populationIndex in range(population.size()):
            individual = population.getFittest(populationIndex)
            #如果是精英就不变异
            if populationIndex >= self.elitismCount:
                
                #遍历基因
                for geneIndex in range(individual.getChromosomeLength()):
                    if (self.mutationRate > random.random()):
                        #得到要变异的位置
                        newGenePos=int(random.random()*individual.getChromosomeLength())
                        
                        #获取要交换的基因
                        gene1=individual.getGene(newGenePos)
                        gene2=individual.getGene(geneIndex)
                        
                        #交换基因
                        individual.setGene(newGenePos, gene2)
                        individual.setGene(geneIndex, gene1)
                        
            newPopulation.setIndividual(populationIndex, individual)
        return newPopulation
    
    

class TSP():
        
    maxGenerations=3000
    def main(self):
        #随机生成100个城市坐标
        numCities = 100
        cities=[City(int(random.random()*100), int(random.random()*100)) for cityIndex in range(numCities)]
    
        #创建算法对象
        #种群数量，变异率，交叉率，精英成员数
        ga=GeneticAlgorithm(100, 0.001, 0.9, 2, 5)    
        
        #创建种群
        #基因长度等于城市的数量
        population = ga.initPopulation(numCities)    
                
        #评估种群的适应度
        ga.evalPopulation(population, cities)
        
        generation=1        #第几代
    
        #开始进化循环
        while ga.isTerminationConditionMet(generation, self.maxGenerations)==False:
            #打印种群中适应度最好的个体
            route=Route(population.getFittest(0), cities)
            print ("G",generation," Best distance: ", route.getDistance())
    
            #交叉
            population = ga.crossoverPopulation(population)
            
            #突变
            population = ga.mutatePopulation(population)
            
            #评估种群
            ga.evalPopulation(population, cities)
            
            #代数增加
            generation+=1
    
        #打印结果
        print ("Found solution after %d generations" % generation)
        route=Route(population.getFittest(0), cities)
        print ("Best distance: ", route.getDistance())


        
entry=TSP()
entry.main()


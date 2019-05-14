# -*- coding: utf-8 -*-

#Python 3.5.x

import os
import sys
import datetime

import math
import random


__metaclass__ = type


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
    
    def toString(self):
        #将染色体转为可打印字符串
        return "".join([str(item) for item in self.chromosome])


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
    
    def __init__(self, populationSize, mutationRate, crossoverRate, elitismCount):
        self.populationSize=populationSize
        self.mutationRate=mutationRate
        self.crossoverRate=crossoverRate
        self.elitismCount=elitismCount
        return
    
    def initPopulation(self, chromosomeLength):
        return Population(self.populationSize, chromosomeLength)
        
        
    def calcFitness(self, individual):
        #统计个体中1的数量，作为个体的适应度
        individual.setFitness(individual.getChromosome().count(1)/individual.getChromosomeLength())
        return individual.getFitness()
    
    def evalPopulation(self, population):
        #遍历和评估种群中所有个体的适应度
        populationFitness=0.0
        
        for individual in population.getIndividuals():
            populationFitness+=self.calcFitness(individual)
            
        population.setPopulationFitness(populationFitness)
    
    def isTerminatConditionMet(self, population):
        #停止进化/已经进化的足够好的条件
        for individual in population.getIndividuals():
            if individual.getFitness()==1:
                return True
        return False
    
    def selectParent(self, population):
        #选出亲代
        
        individuals=population.getIndividuals()
        
        #用轮盘赌的方式取个体,先构造轮盘
        populationFitness=population.getPopulationFitness()
        rouletteWheelPosition = populationFitness*random.random()
        
        #取出两个个体做父母
        spinWheel=0
        for individual in individuals:
            spinWheel+=individual.getFitness()
            if spinWheel>=rouletteWheelPosition:
                return individual
        
        return individuals[-1]
    
    def crossoverPopulation(self, population):
        #种群基因交叉
        
        #创建新的种群
        newPopulation=Population(population.size(), population.getIndividual(0).getChromosomeLength())
    
        #基于适应度去遍历种群
        for populationIndex in range(population.size()):
            #顺序取每个个体
            parent1=population.getFittest(populationIndex)
            
            #判断是否需要交叉(条件是交叉率约定的概率，以及不属于精英)
            if self.crossoverRate>random.random() and populationIndex >= self.elitismCount:
                #初始化后代
                offspring=Individual(chromosomeLength=parent1.getChromosomeLength())
                
                #基于适应度再找一个亲代
                parent2=self.selectParent(population)
                
                #混合基因组
                for geneIndex in range(parent1.getChromosomeLength()):
                    #以随机的方式混合基因
                    if (0.5 > random.random()):
                        offspring.setGene(geneIndex, parent1.getGene(geneIndex))
                    else:
                        offspring.setGene(geneIndex, parent2.getGene(geneIndex))
                
                #将子代加入新的种群
                newPopulation.setIndividual(populationIndex, offspring)
            else:
                #这个亲代不参加基因混合，直接加入新的种群
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
                


class AllOnesGA():
    def main(self):
        
        #创建算法类
        #种群数量，变异率，交叉率，精英成员数
        ga=GeneticAlgorithm(100, 0.01, 0.95, 2)
        
        #创建种群
        population = ga.initPopulation(50)
        
        #评估种群的适应度
        ga.evalPopulation(population)
        
        generation=1        #第几代
        
        while ga.isTerminatConditionMet(population)==False:
            #打印种群中适应度最好的个体
            print (">>Best solution(%d): " % generation + population.getFittest(0).toString()+" "+str(population.getFittest(0).getFitness()))
            
            #交叉
            population=ga.crossoverPopulation(population)
            
            #突变
            population=ga.mutatePopulation(population)
            
            #评估种群
            ga.evalPopulation(population)

            #代数增加
            generation+=1
            
        #打印结果
        print ("Found solution in %d generations" % generation)
        print ("Best solution: "+ population.getFittest(0).toString())
        
entry=AllOnesGA()
entry.main()
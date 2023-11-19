
import numpy as np
import queue

#generic entity class 
class Entity: 
    def __init__(self, id=-1):
        self.id = id
    
    def isCustomer(self):
        return isinstance(self,Customer)
#customer (arrival, id)
class Customer(Entity):
    def __init__(self, arrivalTime, id=-1) -> None:
        super().__init__(id)
        self.arrivalTime = arrivalTime
        self.departureTime = -1
        self.teller = None #teller who served the customer once they get served
   
    def __repr__(self) -> str:
        return f"Customer({self.id=}, {self.arrivalTime=}, {self.departureTime=}, {self.teller.id=})"

class Teller(Entity): 
    def __init__(self, shiftStart, shiftEnd, lunchStart, avgServiceRate, id=-1):
        super().__init__(id)
        self.avgServiceRate = avgServiceRate
        self.shiftStart = shiftStart
        self.shiftEnd = shiftEnd
        self.lunchStart = lunchStart
        self.busyTime = 0
        self.currentCustomer = None #customer who the teller is currently serving
        self.lunchTaken = False

    def getNextDeparture(self, time):
        if time < self.lunchStart:
            return self.lunchStart
        else:
            return self.shiftEnd
    
    def __repr__(self) -> str:
        return f"Teller({self.shiftStart=}, {self.shiftEnd=}, {self.busyTime=}, {self.currentCustomer=})"


#event (type, time, entity)
#entity is either teller or customer
class Event:
    def __init__(self, eventType: str, eventTime: int, entity: Entity) -> None:
        self.eventType = eventType
        self.eventTime = eventTime
        self.entity = entity

    def isDeparture(self):
        return "departure" in self.eventType
    
    def __repr__(self) -> str: 
        #return f"Event({self.eventType=}, {self.eventTime=}, {self.entity.id=})"
        return f"({self.eventType}, {self.eventTime}, {self.entity.__class__}:{self.entity.id})"

    
    def __str__(self) -> str: 
        return f"({self.eventType}, id:{self.entity.id}, {self.eventTime}, )"

    #comparator functions for priority ordering
    def __lt__(self, other):
        entity1 = self.entity
        entity2 = other.entity
        if entity1.__class__ != entity2.__class__ and self.isDeparture() and other.isDeparture():
            
            if entity1.isCustomer():
                if entity1 == entity2.currentCustomer:
                    return True
            else:
                if entity2 == entity1.currentCustomer:
                    return False
                # if self.clock > entity2.lunchStart : 
                #     nextTellerDeparture = entity2.shiftEnd
                # else: 
                #     nextTellerDeparture = entity2.lunchStart
                
                # if entity1.departureTime < nextTellerDeparture:
                #     return Tru

        # if self.eventType == "customer departure" and other.eventType == "teller departure":
        #     if other.entity.currentCustomer == self.entity and :
        #         return True
        
        # if other.eventType == "customer departure" and self.eventType == "teller departure":
        #     if self.entity.currentCustomer == other.entity:
        #         return False

        return self.eventTime < other.eventTime
        

    def __eq__(self, other):

        return self.eventTime == other.eventTime and self.entity == other.entity

#single queue multiserver
class SQMSSimulation:
    #input parameters are statistical parameters for random generation of interarrival and service time 
    # along with number of customers to serve (stopping criteria of the simulation) 
    def __init__(self, meanArrivalRate, maxArrivalRate, tellerSchedule, closeTime, debug = False) -> None:
        self.meanArrivalRate = meanArrivalRate 
        self.maxArrivalRate = maxArrivalRate
        self.tellerSchedule = tellerSchedule
        self.closeTime = closeTime #stopping criteria - number of total customers to serve
        self.debug = debug

    #define the system state at time 0
    #start simulation
    def start(self):
        #define the system state at time 0
        #simulation time clock
        self.clock = 0
        #system state variables 
        self.numInService = 0 #number of customers currently being served 
        #entity lists
        self.customerQueue = []
        self.availableTellers = [] #list of available tellers
        self.allTellers = [] 
        #future event list
        self.futureEventList = queue.PriorityQueue()
        #statistical accumulators
        self.customersArrived = 0 # number of customers who have arrive in queue
        self.customersServed = 0 #number of customers served, i.e. number of departures
        self.totalQueueLength = 0 #sum of queue length at every minute
        self.totalSystemTime = 0
        self.totalWaitTime = 0 
        self.maxQueueLength = 0 
        self.maxWaitTime = 0

        #add teller arrival and departure to the future event list 
        self.scheduleTellers()
        #create first arrival event
        self.scheduleCustomerArrival()
        #start the simulation
        self.advanceTime()
    
    #print results to console
    def outputResults(self):

        serverUtilization = 0
        for t in self.allTellers:
            serverUtilization += t.busyTime/(t.shiftEnd - t.shiftStart-30)
        serverUtilization /= len(self.allTellers)

        print(f"Customers remaining in queue: %d\n" % len(self.customerQueue))
        print(f"Time-average server utilization: %.2f\n" % serverUtilization)
        print(f"Average system time: %.2f\n" % (self.totalSystemTime/self.customersServed))
        print(f"Average wait time: %.2f\n" % (self.totalWaitTime/self.customersServed))
        print(f"Average queue length %.2f\n" % (self.totalQueueLength/self.closeTime))
   
    #advance the simualtion time - main program function
    def advanceTime(self) -> None:
        while self.clock < self.closeTime:
            #get next event form the future event list
            #since futureEventList is a priority queue based on event time
            #the imminent event will be returned by .get()
            nextEvent = self.futureEventList.get() 
            deltaT = nextEvent.eventTime - self.clock
            
            #update statistical accumulators
            self.totalQueueLength += deltaT * len(self.customerQueue)
            
            #advance time
            self.clock = nextEvent.eventTime 
            
            #handle event
            if nextEvent.eventType == "customer arrival":
                self.handleCustomerArrival(nextEvent)
            elif nextEvent.eventType == "customer departure":
                self.handleCustomerDeparture(nextEvent)
            elif nextEvent.eventType == "scheduled teller departure":
                self.scheduleTellerDeparture(nextEvent)
            elif nextEvent.eventType == "teller arrival":
                self.handleTellerArrival(nextEvent)
            else :
                self.handleTellerDeparture(nextEvent)

        
        self.outputResults()
        
                
    def handleTellerArrival(self, event: Event) -> None:
        teller = event.entity

        if self.debug:
            print(f'Teller "{teller.id}" has arrived at %.2f min' % self.clock)
        #add teller to active teller list 
        self.availableTellers.append(teller)
        # add teller to all teller list if they are starting their shift
        if teller.lunchTaken == False: 
            self.allTellers.append(teller)

        #if there's a customer in the queue, serve them
        if len(self.customerQueue) > 0:
            self.scheduleCustomerDeparture()

    def scheduleTellerDeparture(self, event: Event) -> None:
        teller = event.entity

        #if the teller is still serving a customer, 
        #schedule their departure for when the customer departs
        if teller.currentCustomer is None:
            # if the time is the tellers shift end, schedule end fo shift
            if self.clock == teller.shiftEnd: 
                departureTime = teller.shiftEnd
            else: # its lunch time
                departureTime = teller.lunchStart
        else:
            #departure time is one mili minute after customer daprture time 
            departureTime = teller.currentCustomer.departureTime
            if self.debug:
                print(f"{teller.id} was busy\n")

        self.futureEventList.put(Event("teller departure",departureTime, teller)) 

    def handleTellerDeparture(self, event: Event) -> None:
        teller = event.entity
        if teller.lunchTaken == False:
            teller.lunchTaken = True
            #add arrival event to FEL for return from lunch break, 30 minutes later
            self.futureEventList.put(Event("teller arrival",self.clock+30, teller))  
            
        if self.debug:
            print(f"Teller {teller.id} has departed at {self.clock}\n")

        #remove teller from active teller list 
        self.availableTellers.remove(teller)

    def handleCustomerArrival(self, event: Event) -> None:
        customer = event.entity
        
        #increment number of arrivals
        self.customersArrived += 1
        #set customer id
        customer.id = self.customersArrived
       
        if self.debug:
            print(f'Arrival of customer "{customer.id}": %.2f min\n' % self.clock)
        
        #add customer to the queue
        self.customerQueue.append(customer)
        
        #if server is unoccupied, start processing customer 
        if len(self.availableTellers)>0: 
            self.scheduleCustomerDeparture()

        #schedule next arrival 
        self.scheduleCustomerArrival()

        #modify statistical accumulators
        if len(self.customerQueue) > self.maxQueueLength:
            self.maxQueueLength = len(self.customerQueue)

    def handleCustomerDeparture(self, event: Event) -> None:
        customer = event.entity
        teller = customer.teller
        
        #print custer service time
        systemTime = customer.departureTime - customer.arrivalTime
        if self.debug:
            print(f'Total system time for customer "{customer.id}": %.2f min' % systemTime)
            print(f'Served by teller "{teller.id}"\n')
        
        #set tellers currentCustomer to None
        teller.currentCustomer = None
        
        #return teller to available teller list
        self.numInService -= 1
        self.availableTellers.append(teller)

        
        
        #if customer are waiting, schedule next departure
        if teller.lunchTaken == False and self.clock > teller.lunchStart:
            pass
        elif self.clock > teller.shiftEnd:
            pass
        elif len(self.customerQueue) > 0 :
            self.scheduleCustomerDeparture()  
        
        #modify statistical accumulators
        self.customersServed += 1
        self.totalSystemTime += systemTime

    #add arrival of new customer event to the FEL
    def scheduleCustomerArrival(self) -> None:
        #generate arrival time
        if self.customersArrived == 0: #don't generate interaarival for first customer
            arrivalTime = 0
        else:
            arrivalTime = self.clock + self.generateInterarrivalTime()

        #only schedule customer if they arrive before close time of the bank
        if arrivalTime < self.closeTime:
            #add arrival event to the future event list and create an associated customer
            self.futureEventList.put(Event("customer arrival",arrivalTime, Customer(arrivalTime = arrivalTime, )))
    
    #add event for the departure of current customer to the FEL 
    #analogus to serving customer 
    def scheduleCustomerDeparture(self) -> None:
        #get customer at the head of the queue
        customer = self.customerQueue.pop(0)
        waitTime = self.clock - customer.arrivalTime
        #print their wait time 
        if self.debug:
            print(f'Waiting time for customer "{customer.id}": %.2f min' % waitTime)
        
        #update statistical accumulators 
        self.totalWaitTime += waitTime 

        #get available teller
        teller = self.availableTellers.pop(0)
        customer.teller = teller
        teller.currentCustomer = customer
        if self.debug:
            print(f"teller {teller.id} is serving\n")

        #generate customer departure time
        serviceTime = self.generateServiceTime(teller.avgServiceRate)
        departureTime = self.clock+ serviceTime
        customer.departureTime = departureTime

        teller.busyTime += serviceTime

        #add departure event to the FEL
        self.futureEventList.put(Event("customer departure",departureTime, customer))
        self.numInService += 1

    def scheduleTellers(self):
        for t in self.tellerSchedule:

            #add arrival event to the FEL at tellers shift start time
            self.futureEventList.put(Event("teller arrival",t.shiftStart, t))
            #add departure event to FEL to leave for lunch break
            self.futureEventList.put(Event("scheduled teller departure",t.lunchStart, t))  
            #self.futureEventList.put(Event("teller departure",t.lunchStart, t))                           
            #add departure event to FEL for clock out
            self.futureEventList.put(Event("scheduled teller departure",t.shiftEnd, t))
           # self.futureEventList.put(Event("teller departure",t.shiftEnd, t))       

    #generate random interarrival time from normal distribution
    def generateInterarrivalTime(self) -> float:
        
        
        interTime = 0
        while True: 
            #get current avg arrival rate
            arrivalRate = self.meanArrivalRate(self.clock+interTime)
            
            #generate interarrival time E
            E = np.random.default_rng().exponential(1/self.maxArrivalRate)
            
            U = np.random.default_rng().uniform(0,1)
            
            #add E to total interarrival time
            interTime += E

            if U <= arrivalRate/self.maxArrivalRate :
                break
            
            
                
        return interTime
    
    #generate random service time from normal distribution
    def generateServiceTime(self, avgServiceRate) -> float:
        result = np.random.default_rng().exponential(1/avgServiceRate)
        return result





def main():
    lvl1_serviceRate = 0.18
    lvl2_serviceRate = 0.1


    tellerSchedule = [
        #Teller(start,end,lunch,service rate, id)
        Teller(0,8*60,4*60,lvl1_serviceRate,1),
        Teller(2*60,10*60,8*60,lvl2_serviceRate,2),
    ]

    def meanArrivalRate(t): 
        lamda = 0  
        if t > 5 * 6 * 1:
             lamda = 0.1
        elif t > 5 * 6 * 2:
            lamda = 0.18
        elif t > 5 * 6 * 3:
            lamda = 0.26
        elif t > 5 * 6 * 4:
            lamda = 0.375
        elif t > 5 * 6 *5:
            lamda = 0.4
        elif t > 5 * 6 * 6:
            lamda = 0.42
        elif t > 5 * 6 * 7:
            lamda = 0.46
        elif t > 5 * 6 * 8:
            lamda = 0.44
        elif t > 5 * 6 * 9:
            lamda = 0.42
        elif t > 5 * 6 * 10:
            lamda = 0.375
        elif t > 5 * 6 * 11:
            lamda = 0.29
        elif t > 5 * 6 * 12:
            lamda = 0.26
        elif t > 5 * 6 * 13:
            lamda = 0.225
        elif t > 5 * 6 * 14:
            lamda = 0.15
        elif t > 5 * 6 * 15:
            lamda = 0.1
        return lamda

    maxArrivalRate = 0.46
    closeTime = 10 * 60 #10 hours of open time 

    sim = SQMSSimulation(meanArrivalRate, maxArrivalRate, tellerSchedule, closeTime)
    sim.start()


if __name__ == "__main__":
    main()
    
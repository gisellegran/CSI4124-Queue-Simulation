
import numpy as np
import queue

#generic entity class 
class Entity: 
    def __init__(self, id=-1):
        self.id = id
        pass
#customer (arrival, id)
class Customer(Entity):
    def __init__(self, arrivalTime : int, id=-1) -> None:
        super().__init__(id)
        self.arrivalTime = arrivalTime
        self.teller = None #teller who served the customer once they get served

class Teller(Entity): 
    def __init__(self, shift_start, shift_end, avgServiceTime, id=-1):
        super().__init__(id)
        self.avgServiceTime = avgServiceTime
        self.shift_start = shift_start
        self.shift_end = shift_end
        
class Tellers: 
    def __init__(self):
        self.tellers = []
    
    def addTeller(self, teller : Teller):
        self.tellers.append(teller)

    def getAvailableTeller(self):
        for t in self.tellers: 
            if t.isAvailable :
                return t
        return None
    
    #generate random service time from normal distribution
    def generateServiceTime(self) -> float:
        result = np.random.default_rng().normal(self.meanServiceTime, self.sdServiceTime)
        return result

    def serveCustomer(self, customer : Customer):
        #get next available teller 
        teller = self.getAvailableTeller()

        #generate service time based on teller average service time 
        #variance based on variance of tasks
        #avgService time based on teller experience
        return 
        #return service time 


#event (type, time, entity)
#entity is either teller or customer
class Event:
    def __init__(self, eventType: str, eventTime: int, entity: Entity) -> None:
        self.eventType = eventType
        self.eventTime = eventTime
        self.entity = entity

    #comparator functions for priority ordering
    def __gt__(self, other):
        return self.eventTime > other.eventTime

    def __eq__(self, other):
        return self.eventTime == other.eventTime

class SSQSimulation:
    #input parameters are statistical parameters for random generation of interarrival and service time 
    # along with number of customers to serve (stopping criteria of the simulation) 
    def __init__(self, meanArrivalRate, sdServiceTime, tellerSchedule, closeTime) -> None:
        self.meanArrivalRate = meanArrivalRate
        self.sdServiceTime = sdServiceTime #TO DO: find value 
        self.tellerSchedule = tellerSchedule
        self.closeTime = closeTime #stopping criteria - number of total customers to serve

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
        self.tellers = [] #list of available tellers
        #future event list
        self.futureEventList = queue.PriorityQueue()
        #statistical accumulators
        self.customersArrived = 0 # number of customers who have arrive in queue
        self.tellersArrived = 0 #  number of tellers who have clocked in 
        self.customersServed = 0 #number of customers served, i.e. number of departures
        self.totalWaitTime = 0 
        self.maxWaitTime = 0

        #add teller arrival and departure to the future event list 
        self.scheduleTellers()
        #create first arrival event
        self.scheduleArrival()
        #start the simulation
        self.advanceTime()
    
    #advance the simualtion time - main program function
    def advanceTime(self) -> None:
        while self.customersServed < self.customersToServe:
            #get next event form the future event list
            #since futureEventList is a priority queue based on event time
            #the imminent event will be returned by .get()
            nextEvent = self.futureEventList.get() 

            self.clock = nextEvent.eventTime #advance time
            if nextEvent.eventType == "customer arrival":
                self.handleCustomerArrival(nextEvent)
            elif nextEvent.eventType == "customer departure":
                self.handleCustomerDeparture(nextEvent)
            elif nextEvent.eventType == "teller arrival":
                self.handleTellerArrival(nextEvent)
            else :
                self.handleTellerDeparture(nextEvent)
                
    def handleTellerArrival(self, event: Event) -> None:
        teller = event.entity
        if teller.id < 
        #add teller to active teller list 
        self.tellers.append(teller)

        #if there's a customer in the queue, serve them
        if len(self.customerQueue) > 0:
            self.scheduleDeparture()

    def handleTellerDeparture(self, event: Event) -> None:
        teller = event.entity

        #add teller to active teller list 
        self.tellers.remove(teller)

        #if there's a customer in the queue, serve them
        if len(self.customerQueue) > 0:
            self.scheduleDeparture()

    def handleCustomerArrival(self, event: Event) -> None:
        customer = event.customer
        #set customer number
        customer.customerNumber = self.customersArrived+1
        #add customer to the queue
        self.customerQueue.append(customer)
        
        #if server is unoccupied, start processing customer 
        if len(self.tellers)>0: 
            self.scheduleDeparture()

        #increment number of arrivals
        self.customersArrived += 1

        #schedule next arrival 
        self.scheduleCustomerArrival()

    def handleCustomerDeparture(self, event: Event) -> None:
        customer = event.customer
        
        #print custer service time
        systemTime = customer.departureTime - customer.arrivalTime
        print(f'Total system time for customer "{customer.customerNumber}": %.2f sec\n' % systemTime)
        
        #return teller to available teller list
        self.tellers.append(customer.teller)
        self.numInService -= 1
        
        #if customer are waiting, schedule next departure
        if len(self.customerQueue) > 0:
            self.scheduleDeparture()  
        
        self.customersServed += 1

    #add arrival of new customer event to the FEL
    def scheduleCustomerArrival(self) -> None:
        #generate arrival time
        if self.customersArrived == 0: #don't generate interaarival for first customer
            arrivalTime = 0
        else:
            arrivalTime = self.clock + self.generateInterarrivalTime()

        #add arrival event to the future event list and create an associated customer
        self.futureEventList.put(Event("arrival",arrivalTime, Customer(arrivalTime = arrivalTime)))
    
    #add event for the departure of current customer to the FEL 
    #analogus to serving customer 
    def scheduleCustomerDeparture(self) -> None:
        #get customer at the head of the queue
        customer = self.customerQueue.pop(0)
        waitTime = self.clock - customer.arrivalTime
        #print their wait time 
        print(f'Waiting time for customer "{customer.customerNumber}": %.2f sec' % waitTime)

        #get available teller
        teller = self.tellers.pop(0)

        #generate customer departure time
        departureTime = self.clock+self.generateServiceTime(teller.avgServiceTime)
        customer.departureTime = departureTime

        customer.teller = teller

        #add departure event to the FEL
        self.futureEventList.put(Event("departure",departureTime, customer))
        self.numInService += 1

    def scheduleTellers(self):
        for t in self.tellerSchedule:
            #add arrival event to the FEL at tellers shift start time
            shift_start = t.start_time
            shift_end = t.end_time
            #lunch break starts midway through shift
            lunch_start = shift_start+(shift_start-shift_end)/2.0
            #lunch is 30 minutes
            lunch_end = lunch_start + 0.5
            #add arrival event for clock in 
            self.futureEventList.put(Event("teller arrival",shift_start, t))
            #add departure event to FEL to leave for lunch break
            self.futureEventList.put(Event("teller departure",lunch_start, t))        
            #add arrival event to FEL for return from lunch break
            self.futureEventList.put(Event("teller arrival",lunch_end, t))                    
            #add departure event to FEL for clock out
            self.futureEventList.put(Event("teller departure",shift_end, t))      
                                         
    #generate random interarrival time from normal distribution
    def generateInterarrivalTime(self) -> float:
        result = np.random.default_rng().exponential(1/self.meanArrivalRate)
        return result
    
    #generate random service time from normal distribution
    def generateServiceTime(self, avgServiceTime) -> float:
        result = np.random.default_rng().normal(self.avgServiceTime, self.sdServiceTime)
        return result



def main():
    #given project parameters (time in seconds)
    meanInterarrivalTime = 30
    sdInterarrivalTime = 6
    meanServiceTime =  20
    sdServiceTime = 4
    customersToServe = 15

    lvl1_serviceTime = 0.10
    lvl2_serviceTime = 0.20

    tellers = [
        Teller(0,8,lvl1_serviceTime),
        Teller(2,10,lvl2_serviceTime),
    ]

    sim = SSQSimulation(meanInterarrivalTime, sdInterarrivalTime, meanServiceTime, sdServiceTime, customersToServe)
    sim.start()


if __name__ == "__main__":
    main()
    
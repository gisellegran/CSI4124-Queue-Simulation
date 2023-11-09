
import numpy as np
import queue

#customer (arrival, id)
class Customer:
    def __init__(self, arrivalTime : int, customerNumber=-1) -> None:
        self.customerNumber = customerNumber
        self.arrivalTime = arrivalTime

class Teller: 
    def __init__(self, avgServiceTime):
        self.avgServiceTime = avgServiceTime

#event (type, time, customer)
class Event:
    def __init__(self, eventType: str, eventTime: int, customer: Customer) -> None:
        self.eventType = eventType
        self.eventTime = eventTime
        self.customer = customer

    #comparator functions for priority ordering
    def __gt__(self, other):
        return self.eventTime > other.eventTime

    def __eq__(self, other):
        return self.eventTime == other.eventTime

class SSQSimulation:
    #input parameters are statistical parameters for random generation of interarrival and service time 
    # along with number of customers to serve (stopping criteria of the simulation) 
    def __init__(self, meanInterarrivalTime, sdInterarrivalTime,
                 meanServiceTime, sdServiceTime, customersToServe) -> None:
        self.meanInterarrivalTime = meanInterarrivalTime
        self.sdInterarrivalTime = sdInterarrivalTime
        self.meanServiceTime = meanServiceTime
        self.sdServiceTime = sdServiceTime
        self.customersToServe = customersToServe #stopping criteria - number of total customers to serve

    #define the system state at time 0
    #start simulation
    def start(self):
        #define the system state at time 0
        #simulation time clock
        self.clock = 0
        #system state variables 
        self.numInService = 0 #number of customers currently being served 
        #entity (customers) list 
        self.customerQueue = []
        #future event list
        self.futureEventList = queue.PriorityQueue()
        #statistical accumulators
        self.customersArrived = 0 # number of customers who have arrive in queue
        self.customersServed = 0 #number of customers served, i.e. number of departures
        self.totalWaitTime = 0 
        self.maxWaitTime = 0

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
            if nextEvent.eventType == "arrival":
                self.handleArrival(nextEvent)
            else:
                self.handleDeparture(nextEvent)

    def handleArrival(self, event: Event) -> None:
        customer = event.customer
        #set customer number
        customer.customerNumber = self.customersArrived+1
        #add customer to the queue
        self.customerQueue.append(customer)
        
        #if server is unoccupied, start processing customer 
        if self.numInService == 0: 
            self.scheduleDeparture()

        #increment number of arrivals
        self.customersArrived += 1

        #schedule next arrival 
        self.scheduleArrival()

    def handleDeparture(self, event: Event) -> None:
        customer = event.customer
        
        #print custer service time
        systemTime = customer.departureTime - customer.arrivalTime
        print(f'Total system time for customer "{customer.customerNumber}": %.2f sec\n' % systemTime)
        
        #if customer are waiting, schedule next departure
        #otherwise, idle the server
        if len(self.customerQueue) > 0:
            self.scheduleDeparture()
        else:
            self.numInService = 0
        
        self.customersServed += 1

    #add arrival of new customer event to the FEL
    def scheduleArrival(self) -> None:
        #generate arrival time
        if self.customersArrived == 0: #don't generate interaarival for first customer
            arrivalTime = 0
        else:
            arrivalTime = self.clock + self.generateInterarrivalTime()

        #add arrival event to the future event list and create an associated customer
        self.futureEventList.put(Event("arrival",arrivalTime, Customer(arrivalTime = arrivalTime)))
    
    #add event for the departure of current customer to the FEL 
    #analogus to serving customer 
    def scheduleDeparture(self) -> None:
        #get customer at the head of the queue
        customer = self.customerQueue.pop(0)
        waitTime = self.clock - customer.arrivalTime
        #print their wait time 
        print(f'Waiting time for customer "{customer.customerNumber}": %.2f sec' % waitTime)
        #generate customer departure time
        departureTime = self.clock+self.generateServiceTime()
        customer.departureTime = departureTime

        #add departure event to the 
        self.futureEventList.put(Event("departure",departureTime, customer))
        self.numInService = 1

    #generate random interarrival time from normal distribution
    def generateInterarrivalTime(self) -> float:
        result = np.random.default_rng().normal(self.meanInterarrivalTime, self.sdInterarrivalTime)
        return result

    #generate random service time from normal distribution
    def generateServiceTime(self) -> float:
        result = np.random.default_rng().normal(self.meanServiceTime, self.sdServiceTime)
        return result

def main():
    #given project parameters (time in seconds)
    meanInterarrivalTime = 30
    sdInterarrivalTime = 6
    meanServiceTime =  20
    sdServiceTime = 4
    customersToServe = 15

    sim = SSQSimulation(meanInterarrivalTime, sdInterarrivalTime, meanServiceTime, sdServiceTime, customersToServe)
    sim.start()


if __name__ == "__main__":
    main()
    
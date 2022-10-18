import random
from operator import attrgetter

from Entities import TaskTransfer, TaskPick
extra_for_transfer = 1

class Utility:
    def __init__(self, employee,task , i, j, ro=1):

        self.ro = ro
        self.task = task
        self.agent = employee
        self.i = i
        self.j = j
        self.linear_utility = self.calculate_linear_utility()
        self.xij = None

    def get_utility(self, ratio=1):
        return (ratio * self.linear_utility)

    def get_task_name(self):
        if isinstance(self.task, TaskTransfer):
            return "transfer"
        else:
            return "pick"

    def calculate_linear_utility(self):
        # transfer>pick
        task_name = self.get_task_name()
        employee_grade = self.agent.abilities[task_name]
        combo_grade = 0


        if isinstance(self.task, TaskTransfer):
            combo_grade= extra_for_transfer*employee_grade

        #task_type_importance = self.get_task_importance()

        if isinstance(self.task, TaskPick):
            employee_grade = employee_grade / 10
            if self.task.numberOfIdsRatio<0.5 and employee_grade<0.5:
               combo_grade = (1- self.task.numberOfIdsRatio)*(1-employee_grade)
            else:
               combo_grade =self.task.numberOfIdsRatio*employee_grade

        # notice grade of employee for the type of task
        task_importance = self.task.importance

        # marked orders in transfer
        marked_in_transfer = self.get_if_items_of_order_is_in_transfer()

        # importance for pick do random

        if employee_grade == 0:
            return 0

        return (marked_in_transfer*combo_grade)



    def get_if_items_of_order_is_in_transfer(self):
        if isinstance(self.task, TaskPick):
            if self.task.is_in_transfer:
                return 0

        return 1




class FisherDistributed:
    def __init__(self, utilities):
        self.counter = 0
        self.change = 0
        self.THRESHOLD = 1E-8

        self.nofGoods = len(utilities[0])
        self.nofAgents = len(utilities)
        self.utilities_ = [[None for _ in range(self.nofGoods)] for _ in
                           range(self.nofAgents)]  # utilities of buyers over the goods

        self.bids = [[0 for _ in range(self.nofGoods)] for _ in range(self.nofAgents)]  # buyers bids over the goods
        self.prices = [0 for _ in range(self.nofGoods)]  # prices of the goods in the market
        valuation_sums = [0 for _ in range(self.nofAgents)]
        for i in range(self.nofAgents):
            for j in range(self.nofGoods):
                if utilities[i][j] is not None:
                    self.utilities_[i][j] = utilities[i][j]
                    valuation_sums[i] += utilities[i][j].get_utility(1)
            for j in range(self.nofGoods):
                if utilities[i][j] is not None:
                    self.bids[i][j] = utilities[i][j].get_utility(1) / valuation_sums[i]

        self.generateAllocations()
        self.algorithm()

    # generates allocation according to current bids and prices
    def generateAllocations(self):
        for j in range(self.nofGoods):
            self.prices[j] = 0
            for i in range(self.nofAgents):
                self.prices[j] += self.bids[i][j]
        self.change = 0
        for i in range(self.nofAgents):
            for j in range(self.nofGoods):
                if self.prices[j] != 0:
                    if self.utilities_[i][j].xij is not None:
                        self.change += abs(((self.bids[i][j] / self.prices[j]) - self.utilities_[i][j].xij))
                    if self.bids[i][j] / self.prices[j] > 1E-10:
                        self.utilities_[i][j].xij = self.bids[i][j] / self.prices[j]

        # self.print()

    def print_X(self):
        print()
        print("------Matrix X------")

        for i in range(self.nofAgents):
            print()
            for j in range(self.nofGoods):
                if j == 0:
                    print("Agent id_", self.utilities_[i][j].agent.id_, end=":  ")

                if self.utilities_[i][j].xij is not None and self.utilities_[i][j].xij > 0.0000001:
                    if self.utilities_[i][j].xij > 0.99:
                        print("1.00000", end="\t")
                    if self.utilities_[i][j].xij == 0:
                        print("0.00000", end="\t")
                    else:
                        print(round(self.utilities_[i][j].xij, ndigits=5), end="\t")
                else:
                    print("0.00000", end="\t")
        print()

    def iterate(self):
        utilities = [[0 for _ in range(self.nofGoods)] for _ in
                     range(self.nofAgents)]
        # calculate current utilities and sum the utility for each agent
        utilitySum = [0 for _ in range(self.nofAgents)]
        for i in range(self.nofAgents):
            for j in range(self.nofGoods):
                if self.utilities_[i][j].xij is not None:
                    utilities[i][j] = self.utilities_[i][j].get_utility(self.utilities_[i][j].xij)
                    utilitySum[i] += utilities[i][j]

        for i in range(self.nofAgents):
            for j in range(self.nofGoods):
                calc_bid = utilities[i][j] / utilitySum[i]
                flag = False
                if calc_bid < 0.0001:
                    self.bids[i][j] = 0
                    flag = True
                if calc_bid > 0.9999:
                    self.bids[i][j] = 1
                    flag = True
                if not flag:
                    self.bids[i][j] = calc_bid

        self.generateAllocations()


    # algorithm
    def algorithm(self):
        self.iterate()
        while self.isStable() is False:
            self.iterate()
        self.fix_xij()
        return

    def isStable(self):
        self.counter = self.counter + 1
        if self.counter > 5000:
            return True
        #print("change", self.change)
        return self.change < self.THRESHOLD

    def fix_xij(self):
        for i in range(len(self.utilities_)):
            for j in range(len(self.utilities_[i])):
                util = self.utilities_[i][j]
                if util.xij is not None and util.xij<0.05:
                    util.xij = 0





class FisherForUserV2():
    def __init__(self, employees,tasks,tasks_transfer,tasks_pick):
        #self.R_matrix = []
        #self.set_R_matrix(employees, tasks)
        #self.fmc = FisherDistributed(self.R_matrix)
        #self.X_matrix = []
        #self.create_X_matrix()
        self.employees = employees

        self.schedule = {}
        for employee in employees:
            self.schedule[employee.id_] = []

        self.schedule_tasks_transfer(tasks_transfer)
        self.schedule_tasks_pick(tasks_pick)




    def schedule_tasks_pick(self, tasks_pick):
        tasks_pick = sorted(tasks_pick, key=lambda x: x.numberOfIdsRatio, reverse=True)
        for task_pick in tasks_pick:
            self.place_task_pick(task_pick)


    def schedule_tasks_transfer(self, tasks_transfer):
        tasks_transfer = sorted(tasks_transfer, key=lambda x: x.total_volume, reverse=True)
        for task_transfer in tasks_transfer:
            self.place_task_transfer(task_transfer)

    def place_task_pick(self, task_pick):

        min_id_with_tasks = min(self.schedule.keys(),key=lambda x:len(self.schedule[x]))
        min_amount_of_tasks= len(self.schedule[min_id_with_tasks])

        relevant_employees_ids = self.get_relevant_employees_ids(min_amount_of_tasks,self.schedule)
        relevant_employees = self.get_relevant_employees(relevant_employees_ids,self.employees)
        assigned_employee = max(relevant_employees,key=lambda x: x.abilities["pick"])
        self.schedule[assigned_employee.id_].append(task_pick)

    def get_temp_schedule(self,employees_for_transfer):
        temp_schedule = {}
        for emp in employees_for_transfer:
            temp_schedule[emp.id_] = self.schedule[emp.id_]
        return  temp_schedule


    def get_relevant_employees_ids(self, min_amount_of_tasks, temp_schedule):
        ans = []
        for k, v in temp_schedule.items():
            if len(v) == min_amount_of_tasks:
                ans.append(k)
        return ans


    def get_relevant_employees(self, relevant_employees_ids, employees_for_transfer):
        ans = []
        for id_ in relevant_employees_ids:
            for emp in employees_for_transfer:
                if emp.id_ == id_:
                    ans.append(emp)
        return ans


    def place_task_transfer(self, task_transfer):

        employees_for_transfer = self.get_employees_for_transfer()
        temp_schedule = self.get_temp_schedule(employees_for_transfer)
        min_id_with_tasks = min(temp_schedule.keys(),key=lambda x:len(temp_schedule[x]))
        min_amount_of_tasks= len(temp_schedule[min_id_with_tasks])

        relevant_employees_ids = self.get_relevant_employees_ids(min_amount_of_tasks,temp_schedule)
        relevant_employees = self.get_relevant_employees(relevant_employees_ids,employees_for_transfer)
        assigned_employee = max(relevant_employees,key=lambda x: x.abilities["transfer"])
        self.schedule[assigned_employee.id_].append(task_transfer)

    def get_employees_for_transfer(self):
        ans = []
        for employee in self.employees:
            if employee.abilities["transfer"] > 0:
                ans.append(employee)
        return ans


    def set_R_matrix(self, employees,tasks):

        for i in range(len(employees)):
            single_row = []
            for j in range(len(tasks )):
                util = Utility(employees[i], tasks [j], i, j)
                single_row.append(util)
            self.R_matrix.append(single_row)

    def create_X_matrix(self):
        for i in range(len(self.R_matrix)):
            single_row = []
            for j in range(len(self.R_matrix[0])):
                single_row.append(self.R_matrix[i][j].xij)
            self.X_matrix.append(single_row)














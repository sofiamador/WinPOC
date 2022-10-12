import random

from Entities import TaskTransfer, TaskOrder


class Utility:
    def __init__(self, employee,task , i, j, ro=1):
        self.ratio_is_in_transfer = 0.3
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
        task_type_importance = self.get_task_importance()
        task_name = self.get_task_name()

        # notice grade of employee for the type of task
        employee_grade = self.agent.abilities[task_name]
        employee_grade_threshold = 8
        task_importance = self.task.importance
        task_importance_threshold = 0.5

        comb_grade = 0

        if employee_grade<=employee_grade_threshold and task_importance<=task_importance_threshold:
            comb_grade = 10

        if employee_grade <= employee_grade_threshold and task_importance > task_importance_threshold:
            comb_grade = 0.5

        if employee_grade>employee_grade_threshold and task_importance<=task_importance_threshold:
            comb_grade = 0.5

        if employee_grade>employee_grade_threshold and task_importance>task_importance_threshold:
            comb_grade = 10



        # marked orders in transfer
        marked_in_transfer = self.get_if_items_of_order_is_in_transfer()

        # importance for pick do random

        if employee_grade == 0:
            return 0

        return (task_type_importance * marked_in_transfer*comb_grade)

    def get_task_importance(self):
        ans = 1
        if isinstance(self.task, TaskTransfer):
            ans = 10
        return ans

    def get_if_items_of_order_is_in_transfer(self):
        if isinstance(self.task, TaskOrder):
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
    def __init__(self, employees,tasks):
        self.R_matrix = []
        self.set_R_matrix(employees, tasks)
        self.fmc = FisherDistributed(self.R_matrix)
        self.X_matrix = []
        self.create_X_matrix()
        # for i in range(len(self.X_matrix)):
        #    print()
        #    for j in range (len(self.X_matrix[i])):
        #        print(self.X_matrix[i][j],end = ",")

    def set_R_matrix(self, employees,tasks ):

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

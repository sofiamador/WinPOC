
class Utility:
    def __init__(self, util=-1,ro=1, ):
        self.ro = ro
        self.linear_utility = util
        self.xij = None

    def get_utility(self, ratio=1):
        return (ratio * self.linear_utility) ** self.ro


class FisherCentralizedImplementation:
    def __init__(self, utilities):
        self.NCLO = 0
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
                    self.NCLO = self.NCLO+1
            for j in range(self.nofGoods):
                if utilities[i][j] is not None:
                    self.bids[i][j] = utilities[i][j].get_utility(1) / valuation_sums[i]
                    self.NCLO = self.NCLO+1

        self.generateAllocations()

    # generates allocation according to current bids and prices
    def generateAllocations(self):
        self.calculate_prices_initial()
        self.calculate_x_ij()

    def calculate_x_ij(self):
        self.change = 0
        for i in range(self.nofAgents):
            for j in range(self.nofGoods):
                if self.prices[j] != 0:
                    if self.utilities_[i][j].xij is None:
                        self.change = 9999999
                    else:
                        self.change += abs(((self.bids[i][j] / self.prices[j]) - self.utilities_[i][j].xij))

                    if self.bids[i][j] / self.prices[j] > 1E-10:
                        self.utilities_[i][j].xij = self.bids[i][j] / self.prices[j]
                        self.NCLO = self.NCLO + 1

        # self.print()

    def calculate_prices_initial(self):
        for j in range(self.nofGoods):
            self.prices[j] = 0
            for i in range(self.nofAgents):
                self.NCLO = self.NCLO + 1
                self.prices[j] += self.bids[i][j]

    def print_xij(self):
        print()
        print("------Matrix X------")

        for i in range(self.nofAgents):
            print()
            for j in range(self.nofGoods):
                if j == 0:
                    print("Agent id_", self.utilities_[i][j].agent.agent_id_, end=":  ")

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
        self.calculate_sum_r_i(utilities,utilitySum)
        self.calculate_bids(utilities,utilitySum)

        self.generateAllocations()

    def calculate_sum_r_i(self, utilities, utilitySum):

        for i in range(self.nofAgents):
            for j in range(self.nofGoods):
                if self.utilities_[i][j].xij is not None:
                    utilities[i][j] = self.utilities_[i][j].getUtility(self.utilities_[i][j].xij)
                    utilitySum[i] += utilities[i][j]
                    self.NCLO += 1

    def calculate_bids(self,utilities,utilitySum):
        for i in range(self.nofAgents):
            for j in range(self.nofGoods):
                calc_bid = utilities[i][j] / utilitySum[i]
                self.NCLO+=1
                flag = False
                if calc_bid < 0.0001:
                    self.bids[i][j] = 0
                    flag = True
                if calc_bid > 0.9999:
                    self.bids[i][j] = 1
                    flag = True
                if not flag:
                    self.bids[i][j] = calc_bid


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
        # print("change", self.change)
        return self.change < self.THRESHOLD

    def fix_xij(self):
        for i in range(len(self.utilities_)):
            for j in range(len(self.utilities_[i])):
                util = self.utilities_[i][j]
                if util.xij<0.05:
                    util.xij = 0

class FisherForUser():
    def __init__(self,utilities_numbers):
        self.R_matrix =[]
        self.set_R_matrix(utilities_numbers)
        self.fmc = FisherCentralizedImplementation(self.R_matrix)
        self.X_matrix = []
        self.create_X_matrix()


    def set_R_matrix(self, utilities_numbers):
        for i in range(len(utilities_numbers)):
            single_row = []
            for j in  range(len(utilities_numbers[0])):
                single_row.append(Utility(utilities_numbers[i][j]))
            self.R_matrix.append(single_row)

    def create_X_matrix(self):
        for i in  range(len(self.R_matrix)):
            single_row = []
            for j in  range(len(self.R_matrix[0])):
                single_row.append(self.R_matrix[i][j].xij)
            self.X_matrix.append(single_row)

def create_X_matrix (R_matrix):
    return FisherForUser(R_matrix).X_matrix

if __name__ == '__main__':
    R_m = [[123,321],[252,400]]
    print(create_X_matrix(R_m))
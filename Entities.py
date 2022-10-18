import random


class Location():
    def __init__(self, loc):
        self.loc_str = loc
        self.warehouse_id = "M"
        if len(loc) > 2 and (loc[2] == "-" or loc[1] == "-"):
            l = loc.split("-")
            self.aisle1 = l[0]
            self.column = int(l[1])
            self.row = int(l[2])
        else:
            self.aisle1 = loc[0]
            if len(loc) > 2:
                self.aisle2 = loc[1]
            if len(loc) > 2:
                self.column = int(loc[2])
            else:
                self.column = None

            if len(loc) > 3:
                self.row = int(loc[3])
            else:
                self.row = None

    def __str__(self):
        return self.loc_str


class Line(object):

    def __init__(self, order_id, item_id, quantity, is_to_price, location_string, importance=0, volume=0):
        """

        :param order_id: order_id that the line belongs to
        :param item_id:
        :param quantity:
        :param is_to_price: should price be added to the product
        :param location_string: full location of the product in the warehouse
        :param importance:
        :param volume: the volume of the products in this line
        """
        self.location = Location(loc=location_string)
        self.quantity = quantity
        self.item_id = item_id
        self.order_id = order_id
        self.is_to_price = is_to_price
        self.volume = volume
        self.importance = importance

def calc_total_volume(lines):
    sum_volume = 0
    for line in lines:
        sum_volume = sum_volume + line.volume
    return sum_volume



def calc_total_volume_of_grouped_items(grouped_items):
    sum_volume = 0
    for grouped in grouped_items:
        sum_volume = sum_volume + grouped.total_volume
    return sum_volume

def calc_total_quantity(lines):
    sum_quantity = 0
    for line in lines:
        sum_quantity = sum_quantity + line.quantity
    return sum_quantity



class Task:
    def __init__(self ):
        self.lines = []
        self.importance = 1


class TaskTransfer(Task):
    def __init__(self,  grouped_items, aisles):
        Task.__init__(self)
        self.aisles = aisles
        self.grouped_items = grouped_items
        self.total_volume = calc_total_volume_of_grouped_items(grouped_items)
        for group in grouped_items:
            self.add_group_to_lines(group)

    def __str__(self):
        return str(self.aisles)+ ", "+ str(self.total_volume)


    def add_another_group(self,group):
        self.grouped_items.append(group)
        self.total_volume = self.total_volume + group.total_volume
        self.add_group_to_lines(group)

    def add_group_to_lines(self, group):
        for line in group.lines:
            self.lines.append(line)


class TaskPick(Task):
    def __init__(self, id_, lines):
        Task.__init__(self)
        self.lines = lines
        self.id_ = id_
        self.importance = random.Random(id_).random()#lines[0].importance
        self.total_volume = calc_total_volume(lines)
        self.number_of_lines = len(lines)
        self.is_in_transfer= False
        self.numberOfIds = self.getNumberOfIds();

    def getNumberOfIds(self):
        ids_ = []
        for line in self.lines:
            if line.item_id not in ids_:
                ids_.append(line.item_id)
        return len(ids_)



class GroupByIsle:
    def __init__(self, isle_id, lines):
        self.lines = lines
        self.isle_id = isle_id
        self.total_volume = calc_total_volume(lines)
        self.number_of_lines = len(lines)

    #def __str__(self):
    #    return lines[0].
class GroupOfItem():
    def __init__(self, item_id, lines):
        self.lines = lines
        self.item_id = item_id
        self.importance = 1 # data not avaliable
        self.total_quantity = calc_total_quantity(lines)
        self.total_volume = calc_total_volume(lines)
        self.number_of_lines = len(lines)  # number of distinct orders\
        self.location = lines[0].location
        self.aisle1 = lines[0].location.aisle1

    def __str__(self):
        return str(self.item_id)+ "  "+ str(self.total_volume)

    def __hash__(self):
        return self.item_id

    def __eq__(self, other):
        return self.item_id == other.item_id


class Employee():

    def __init__(self, id_, abilities):
        self.abilities = abilities
        #self.location = location
        #self.name = name
        self.id_ = id_
    def __str__(self):
        return str(self.id_) + "  " + str(self.abilities)

def calc_distance(location1, location2):
    pass

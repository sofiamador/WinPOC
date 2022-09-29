class Location():
    def __init__(self, loc):
        self.loc_str = loc
        self.warehouse_id = "M"
        if len(loc) > 2 and (loc[2] == "-" or loc[1] == "-"):
            l = loc.split("-")
            self.aisle = l[0]
            self.column = int(l[1])
            self.row = int(l[2])
        else:
            self.aisle = loc[0:2]
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



class Order:
    def __init__(self, id_, priority, lines):
        self.lines = []
        self.id_ = id_
        self.priority = 1
        self.total_volume = 0


class Task:

    def __init__(self, aisle, type_="PIK"):
        self.aisle = aisle
        self.lines = []
        self.type_ = type_
        self.priority = 1
        self.total_quantity = 0
        self.total_volume = 0
        self.number_of_agents_required = 1

    def __str__(self):
        return self.aisle


class Employee():

    def __init__(self, id_, name, location, abilities):
        self.abilities = abilities
        self.location = location
        self.name = name
        self.id_ = id_


def calc_distance(location1, location2):
    pass

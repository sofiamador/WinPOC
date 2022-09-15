class Location():
    def __init__(self, loc):
        self.loc_str = loc
        self.area = "M"
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

    def __init__(self, type_, order_id, inside_order_id, catalog_number, barcode, quantity, warehouse_id, route,
                 is_to_price, package_type, location_string, customer_id):
        """

        :param type_: the type of the order
        :param order_id: order_id that the line belongs to
        :param inside_order_id: order id inside the warehouse
        :param catalog_number:
        :param barcode:
        :param quantity:
        :param warehouse_id:
        :param route: the route of the order (1-9)
        :param is_to_price: should price be added to the product
        :param package_type: [2,3,5,8]
        :param location: full location of the product in the warehouse
        :param row_location: only the row whre the product is located
        :param customer_id: customer id that the line belongs to
        """
        self.customer_id = customer_id
        self.location = Location(loc=location_string)
        self.route = route
        self.warehouse_id = warehouse_id
        self.quantity = quantity
        self.barcode = barcode
        self.catalog_number = catalog_number
        self.inside_order_id = inside_order_id
        self.order_id = order_id
        self.type_ = type_
        self.is_to_price = is_to_price
        self.package_type = package_type
        self.volume = None
        self.importance = 1


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

    def __init__(self,id_, name, location, abilities):
        self.abilities = abilities
        self.location = location
        self.name = name
        self.id_ = id_



def calc_distance(location1,location2):
    pass

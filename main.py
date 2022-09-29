import pandas as pd

from Entities import Line, Task, GroupOfItem, Order


# def get_ailse_name(row):
#     st = row['מאיתור']
#     result = re.findall(pattern="^[A-Z]+", string=st)
#     return result[0]


def read_input(file_name):
    d = pd.read_excel(file_name, index_col=None, dtype="str")
    return d


def choose_records(data_, field_name, value):
    data_2 = data_[data_[field_name] == value]
    return data_2


def create_lines(dic_items_with_volume, lines_input_):
    lines = []
    for ind in lines_input_.index:
        order_id = lines_input_['הזמנה'][ind]
        item_id = lines_input_['מקט'][ind]
        quantity = int(lines_input_['כמות מתוכננת'][ind])
        is_to_price = lines_input_['הערה'][ind] == "תמחור"
        location = lines_input_['מאיתור'][ind]
        importance = lines_input_['עדיפות'][ind]
        volume = quantity * dic_items_with_volume.get(item_id, 0)
        line = Line(order_id=order_id, quantity=quantity, is_to_price=is_to_price, location_string=location,
                    volume=volume,
                    item_id=item_id, importance=importance)
        lines.append(line)
    return lines


def create_dict_of_items(items_input_):
    dic_ = {}
    for ind in items_input_.index:
        item_id = items_input_['מקט'][ind]
        volume = float(items_input_['נפח'][ind])
        dic_[item_id] = volume
    return dic_


def gropup_by_column(lines_input2, column_name):
    pass


def get_lines_by_order(lines):
    dict_ = {}
    for line in lines:
        order_id = line.order_id
        if order_id not in dict_.keys():
            dict_[order_id] = []
        dict_[order_id].append(line)

    ans = []
    counter = 0
    for line_list in dict_.values():
        ans.append(Order(id_=counter, lines=line_list))

    return ans


def get_lines_by_item(lines):
    dict_ = {}
    for line in lines:
        item_id = line.item_id
        if item_id not in dict_.keys():
            dict_[item_id] = []
        dict_[item_id].append(line)

    ans = []
    for line_list in dict_.values():
        ans.append(GroupOfItem(item_id=line_list[0].item_id, lines=line_list))

    return ans


items_input = read_input("volume.xlsx")
dic_items_with_volume = create_dict_of_items(items_input)
lines_input = read_input("input.xlsx")
# print(lines_input.info)
date = "2022-06-19 00:00:00"
lines_input2 = choose_records(lines_input, field_name="תאריך", value=date)
lines_input3 = choose_records(lines_input2, field_name="אזור במחסן", value="M")
# print(lines_input2.info)
group_data = lines_input3.groupby(["מקט"], sort=True)["מקט"].count()
lines = create_lines(dic_items_with_volume, lines_input3)

orders = get_lines_by_order(lines)
item_groups = sorted(get_lines_by_item(lines), key=lambda x: x.number_of_lines, reverse=True)


print(item_groups)

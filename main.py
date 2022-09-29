import pandas as pd
import re
from Entities import Line, Task


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


def create_lines_and_classify_by_item(dic_items_with_volume, lines_input_):
    lines_by_items = {}

    for ind in lines_input_.index:
        order_id = lines_input_['הזמנה'][ind]
        item_id = lines_input_['מקט'][ind]
        quantity = int(lines_input_['כמות מתוכננת'][ind])
        is_to_price = lines_input_['הערה'][ind] == "תמחור"
        location = lines_input_['מאיתור'][ind]
        volume = quantity * dic_items_with_volume.get(item_id,0)
        line = Line(order_id=order_id, quantity=quantity, is_to_price=is_to_price, location_string=location,
                    volume=volume,
                    item_id=item_id)
        if item_id in lines_by_items:
            lines_by_items[item_id].append(line)
        else:
            lst = [line]
            lines_by_items[item_id] = lst
    return lines_by_items


def create_dict_of_items(items_input_):
    dic_ = {}
    for ind in items_input_.index:
        item_id = items_input_['מקט'][ind]
        volume = float(items_input_['נפח'][ind])
        dic_[item_id] = volume
    return dic_

def gropup_by_column(lines_input2, column_name):
    pass


items_input = read_input("volume.xlsx")
dic_items_with_volume = create_dict_of_items(items_input)
lines_input = read_input("input.xlsx")
#print(lines_input.info)
date = "2022-06-19 00:00:00"
lines_input2 = choose_records(lines_input, field_name="תאריך", value=date)
#print(lines_input2.info)
group_data = lines_input2.groupby(["מקט"],sort=True)["מקט"].count()
#lines_by_item = create_lines_and_classify_by_item(dic_items_with_volume, lines_input2)
print(group_data)

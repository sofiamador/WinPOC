import pandas as pd
import re
from Entities import Line, Task


def get_ailse_name(row):
    st = row['מאיתור']
    result = re.findall(pattern="^[A-Z]+", string=st)
    return result[0]


def read_input(file_name):
    d = pd.read_excel(file_name, index_col=0)
    # d['מעבר'] = d.apply(get_ailse_name, axis=1)
    return d


def choose_area(area, data_):
    data_2 = data_[data_['תאור אזור במחסן'] == 'איזור ראשי']
    return data_2


def classify_lines_to_aisle(data_):
    ailses = {}
    for ind in data_.index:
        type_ = data_['סוג משימת מחסן'][ind]
        order_id = data_['הזמנה'][ind]
        inside_order_id = data_['מספר משימת מחסן'][ind]
        catalog_number = data_['מקט'][ind]
        barcode = data_['ברקוד'][ind]
        quantity = data_['כמות מתוכננת'][ind]
        warehouse_id = data_['אזור במחסן'][ind]
        route = data_['קוד קו חלוקה'][ind]
        is_to_price = data_['הערה'][ind] == "תמחור"
        package_type = data_['קוד סוג אריזה'][ind]
        location = data_['מאיתור'][ind]
        customer_id = data_['מס. לקוח'][ind]
        line = Line(type_=type_, order_id=order_id, inside_order_id=inside_order_id, catalog_number=catalog_number,
                    barcode=barcode, quantity=quantity, warehouse_id=warehouse_id, route=route, is_to_price=is_to_price,
                    package_type=package_type, location_string=location, customer_id=customer_id)
        t = ailses.get(line.location.aisle, Task(line.location.aisle))
        t.lines.append(line)
        ailses[line.location.aisle] = t
    return list(ailses.values())


data = read_input("input.xlsx")
data2 = choose_area('איזור ראשי', data)
tasks = classify_lines_to_aisle(data2)
print(tasks)
print("hello")

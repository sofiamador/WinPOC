import pandas as pd

from Entities import Line, GroupOfItem, TaskPick, GroupByIsle, TaskTransfer, Employee

is_with_transfer_tasks = True
orders_to_remove = []
max_groups_per_task_transfer = 4
max_transfer_task= 2
max_volume=1.728




# def get_ailse_name(row):
#     st = row['מאיתור']
#     result = re.findall(pattern="^[A-Z]+", string=st)
#     return result[0]
from Fisher import FisherForUser
from FisherV2 import FisherForUserV2
from FunctionsForMain import read_input, create_employees, create_dict_of_items, create_files_by_date, choose_records, \
    create_lines, get_lines_by_order, get_lines_by_item, get_item_groups_by_aisle, mark_orders, \
    get_orders_not_in_transfer, create_numberOfIdsRatio, remove_pick_tasks_that_are_finished, gather_tasks, \
    create_pandas_ourput, write_to_excel

####------------AGENTS DATA--------------------
employees_data = read_input("employees.xlsx")
employees = create_employees(employees_data)

####------------TASKS DATA--------------------
items_input = read_input("volume.xlsx")
dic_items_with_volume = create_dict_of_items(items_input)
# lines_input = read_input("input.xlsx")
# create_files_by_date(lines_input)
# print(lines_input.info)
date = "2022-06-20"
dir = "input_by_date/"
lines_input = read_input(dir + "input_" + date + ".xlsx")
# lines_input2 = choose_records(lines_input, field_name="תאריך", value=date)
lines_input3 = choose_records(lines_input, field_name="אזור במחסן", value="M")
lines_input4 = choose_records(lines_input3, field_name="קוד קו חלוקה", value="3")
# print(lines_input2.info)
lines = create_lines(dic_items_with_volume, lines_input4)
pick_tasks = get_lines_by_order(lines)
item_groups = get_lines_by_item(lines)
if is_with_transfer_tasks:
    transfer_tasks = get_item_groups_by_aisle(item_groups=item_groups, max_groups_per_task=max_groups_per_task_transfer,
                                              max_transfer_task=max_transfer_task, max_volume=max_volume)
else:
    transfer_tasks = []


pick_tasks = mark_orders(pick_tasks, transfer_tasks)
pick_tasks = get_orders_not_in_transfer(pick_tasks)
create_numberOfIdsRatio(pick_tasks)
pick_tasks = remove_pick_tasks_that_are_finished(pick_tasks)
tasks = gather_tasks(pick_tasks, transfer_tasks)

####------------FISHER--------------------

fisher_user = FisherForUserV2(employees, tasks, transfer_tasks, pick_tasks)
schedule = fisher_user.schedule

####--------Output-----------######
# output = {}
# output[employees[0]] = [tasks[0],tasks[-1]]
# output[employees[1]] = [tasks[1],tasks[1],tasks[-2]]


first = True
for employee in schedule:
    pd_output = create_pandas_ourput(schedule[employee])
    write_to_excel(employee,pd_output,first)
    first = False
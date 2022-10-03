import pandas as pd

from Entities import Line, Task, GroupOfItem, TaskOrder, GroupByIsle, TaskTransfer, Employee


# def get_ailse_name(row):
#     st = row['מאיתור']
#     result = re.findall(pattern="^[A-Z]+", string=st)
#     return result[0]
from Fisher import FisherForUser


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
        ans.append(TaskOrder(id_=counter, lines=line_list))

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


def get_isle_by_item(lines):
    dict_ = {}
    for line in lines:
        aisle1 = line.location.aisle1
        if aisle1 not in dict_.keys():
            dict_[aisle1] = []
        dict_[aisle1].append(line)

    ans = []
    for line_list in dict_.values():
        ans.append(GroupByIsle(isle_id=line_list[0].location.aisle1, lines=line_list))
    return ans


def create_files_by_date(df):
    dates = df["תאריך"].unique()
    for date in dates:
        df_for_date = df[df["תאריך"] == date]
        date_no_time = date.split(" ")[0]
        df_for_date.to_excel("input_" + date_no_time + ".xlsx", sheet_name=date_no_time)


def get_dict_by_aisle(item_groups):
    ans = {}
    for item_group in item_groups:
        item_aisle = item_group.aisle1
        if item_aisle not in ans.keys():
            ans[item_aisle] = []
        ans[item_aisle].append(item_group)
    return ans


def get_aisle_couples():
    return {
        "F": "G",
        "G": "F",
        "H": "I",
        "I": "H",
        "J": "K",
        "K": "J",
        "L": "M",
        "M": "L",
        "N": "O",
        "O": "N",
        "P": "Q",
        "Q": "R",
        "R": None,
        "S": "T",
        "T": "S",
        "U": "V",
        "V": "U",
        "W": "X",
        "X": "W",
        "Y": "Z",
        "Z": "Y",
    }


def get_dict_by_aisle_connection(dict_by_aisle, aisle_couples):
    aisle_used = []
    ans = {}
    for k, v in dict_by_aisle.items():
        if k not in aisle_used:
            aisle_used.append(k)
            try:
                aisle_connection = aisle_couples[k]
                if aisle_connection is not None:
                    if aisle_connection in aisle_used:
                        raise Exception("something in manually placing couples is wrong")
                    aisle_used.append(aisle_connection)
                    expend_group = []
                    for group in dict_by_aisle[k]:
                        expend_group.append(group)
                    for group in dict_by_aisle[aisle_connection]:
                        expend_group.append(group)
                    ans[k + "+" + aisle_connection] = expend_group
                else:
                    ans[k] = dict_by_aisle[k]
            except:
                ans[k] = dict_by_aisle[k]
                print(k, "aisle not in map")

    return ans


def get_sorted_value_list_by_volume(dict_by_aisle_connection):
    ans = {}
    for k, v in dict_by_aisle_connection.items():
        ans[k] = sorted(v, key=lambda x: x.total_volume, reverse=True)
    return ans


def get_transfer_groups_per_aisle(dict_sorted_value_by_volume, max_items_per_group, max_volume):
    ans = {}
    for k, v in dict_sorted_value_by_volume.items():
        ans[k] = []
        counter = max_items_per_group
        volume_sum = 0
        grouped_items_for_task = []

        for item_group in v:

            if volume_sum + item_group.total_volume > max_volume or counter == 0:
                ans[k].append(TaskTransfer(grouped_items_for_task, k))
                counter = max_items_per_group - 1
                volume_sum = item_group.total_volume
                grouped_items_for_task = [item_group]

            else:
                counter = counter - 1
                volume_sum = volume_sum + item_group.total_volume
                grouped_items_for_task.append(item_group)

        if len(grouped_items_for_task) != 0:
            ans[k].append(TaskTransfer(grouped_items_for_task, k))
    return ans


def get_transfer_groups_list(transfer_groups_per_aisle):
    ans = []
    for v in transfer_groups_per_aisle.values():
        for task in v:
            ans.append(task)
    return ans


def select_transfer_tasks(transfer_groups_list_sorted,max_transfer_task):
    ans = []
    for transfer_task in transfer_groups_list_sorted:
        ans.append(transfer_task)
        max_transfer_task = max_transfer_task - 1
        if max_transfer_task == 0:
            break
    return ans


def fix_selected_transfer_tasks(selected_transfer_tasks,dict_sorted_value_by_volume,max_groups_per_task,max_volume):
    list_of_grouped_transfer_tasks = []
    for task in selected_transfer_tasks:
        for group in task.grouped_items:
            list_of_grouped_transfer_tasks.append(group)

    for task in selected_transfer_tasks:

        groups_in_aisle = dict_sorted_value_by_volume[task.aisles]
        while len(task.grouped_items) < max_groups_per_task:
            for group in groups_in_aisle:
                if group not in list_of_grouped_transfer_tasks:
                    if group.total_volume + task.total_volume < max_volume:
                        list_of_grouped_transfer_tasks.append(group)
                        task.add_another_group(group)
                        if len(task.grouped_items) < max_groups_per_task:
                            break

    return selected_transfer_tasks

def get_item_groups_by_aisle(item_groups, max_groups_per_task, max_transfer_task, max_volume):
    dict_by_aisle = get_dict_by_aisle(item_groups)
    aisle_couples = get_aisle_couples()
    dict_by_aisle_connection = get_dict_by_aisle_connection(dict_by_aisle, aisle_couples)
    dict_sorted_value_by_volume = get_sorted_value_list_by_volume(dict_by_aisle_connection)
    transfer_groups_per_aisle = get_transfer_groups_per_aisle(dict_sorted_value_by_volume, max_groups_per_task,
                                                              max_volume)
    transfer_groups_list = get_transfer_groups_list(transfer_groups_per_aisle)
    transfer_groups_list_sorted = sorted(transfer_groups_list, key=lambda x: x.total_volume, reverse=True)

    #--------------
    selected_transfer_tasks = select_transfer_tasks(transfer_groups_list_sorted,max_transfer_task)
    selected_transfer_tasks = fix_selected_transfer_tasks(selected_transfer_tasks,dict_sorted_value_by_volume,max_groups_per_task,max_volume)
    return selected_transfer_tasks




def create_employees(employees_data):
    employees_ = []
    for ind in employees_data.index:
        employee_id = employees_data['שם משתמש'][ind]
        pick_grade = int(employees_data['ליקוט'][ind])
        transfer_grade = int(employees_data['העברה'][ind])
        abilities = {"pick": pick_grade, "transfer": transfer_grade}
        employee = Employee(id_=employee_id, abilities=abilities)
        employees_.append(employee)
    return employees_


def get_items_in_transfer(transfer_tasks):
    ans = []
    for task in transfer_tasks:
        for group in task.grouped_items:
            item_id = group.item_id
            if item_id not in ans:
                ans.append(group.item_id)

    return ans


def mark_orders(order_groups, transfer_tasks):
    items_in_transfer = get_items_in_transfer(transfer_tasks)
    in_transfer_list = []
    for order in order_groups:
        for line in order.lines:
            if line.item_id in items_in_transfer:
                order.is_in_transfer = True
                in_transfer_list.append(order)
                break
    return order_groups,in_transfer_list


def gather_tasks(order_tasks, transfer_tasks):
    tasks = []
    for task in order_tasks:
        tasks.append(task)
    for task in transfer_tasks:
        tasks.append(task)
    return tasks

def create_pandas_ourput(output_tasks):
    quantity_lst = []
    item_id_lst = []
    order_id_lst= []
    for task in output_tasks:
        for l in task.lines:
            quantity_lst.append(l.quantity)
            item_id_lst.append(l.item_id)
            order_id_lst.append(l.order_id)
        quantity_lst.append("000")
        item_id_lst.append("000")
        order_id_lst.append("000")
    d = {'מקט': item_id_lst, 'מספר הזמנה': order_id_lst,"כמות":quantity_lst}
    df = pd.DataFrame(data=d)
    return df



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
order_tasks = get_lines_by_order(lines)
item_groups = get_lines_by_item(lines)
transfer_tasks = get_item_groups_by_aisle(item_groups=item_groups, max_groups_per_task=4,
                                          max_transfer_task=5, max_volume=1.728)
order_tasks, in_transfer_list = mark_orders(order_tasks, transfer_tasks)
tasks = gather_tasks(order_tasks, transfer_tasks)


####------------FISHER--------------------

fisher_user = FisherForUser(tasks, employees)

fisher_user.fmc.print_R()

fisher_user.fmc.print_X()

####--------Output-----------######
output = {}
output[employees[0]] = [tasks[0],tasks[-1]]
output[employees[1]] = [tasks[1],tasks[1],tasks[-2]]


def write_to_excel(employee_id, pd_output, first):
    if first:
        pd_output.to_excel("output.xlsx",
                     sheet_name=employee_id, index=False)
        return
    writer = pd.ExcelWriter("output.xlsx")
    pd_output.to_excel(writer, sheet_name=employee_id, index=False)
    # with pd.ExcelWriter('output.xlsx',mode='a') as writer:
    #     pd_output.to_excel(writer, sheet_name=employee_id)

first = True
for employee in output:
    pd_output = create_pandas_ourput(output[employee])
    write_to_excel(employee.id_,pd_output,first)
    first = False
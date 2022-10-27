import pandas as pd

from Entities import Line, GroupOfItem, TaskTransfer, Employee, GroupByIsle, TaskPick


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
        ans.append(TaskPick(id_=line_list[0].order_id, lines=line_list))

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
    for order in order_groups:
        for line in order.lines:
            if line.item_id in items_in_transfer:
                order.is_in_transfer = True
                break
    return order_groups


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
    type_lst = []
    for task in output_tasks:
        for l in task.lines:
            quantity_lst.append(l.quantity)
            item_id_lst.append(l.item_id)
            order_id_lst.append(l.order_id)
            if isinstance(task,TaskPick):
                type_lst.append("ליקוט")
            else:
                type_lst.append("העברה")
        quantity_lst.append("000")
        item_id_lst.append("000")
        order_id_lst.append("000")
        type_lst.append("000")
    d = {'מקט': item_id_lst, 'מספר הזמנה': order_id_lst,"כמות":quantity_lst,"סוג":type_lst}
    df = pd.DataFrame(data=d)
    return df

def get_orders_not_in_transfer(order_tasks):
    ans = []
    for order_task in order_tasks:
        if order_task.is_in_transfer == False:
            ans.append(order_task)
    return ans


def create_numberOfIdsRatio(order_tasks):
    def get_number_of_ids(task):
        return task.numberOfIds

    max_ids_order = max(order_tasks, key=get_number_of_ids)
    max_ids = max_ids_order.numberOfIds
    for order_task in order_tasks:
        order_task.numberOfIdsRatio = order_task.numberOfIds / max_ids


def get_list_of_pick_ids_to_delete():
    pand_table = read_input("finished_tasks.xlsx")
    temp_ = pand_table["order_ids_to_remove"]
    temp2_ = []
    for i in range(len(temp_)):
        temp2_.append(pand_table["order_ids_to_remove"][i])
    return temp2_


def get_task_by_id(id_to_delete,pick_tasks):
    for task in pick_tasks:
        if task.id_ == id_to_delete:
            return task




def remove_pick_tasks_that_are_finished(pick_tasks):
    list_of_pick_ids_to_delete = get_list_of_pick_ids_to_delete()
    to_remove = []
    for id_to_delete in list_of_pick_ids_to_delete:
        the_task = get_task_by_id(id_to_delete,pick_tasks)
        if the_task is None:
            print(id_to_delete, "was not found and was not deleted")
        else:
            to_remove.append(the_task)
    ans = []
    for task in pick_tasks:
        if task not in to_remove:
            ans.append(task)
    return ans


def write_to_excel(employee_id, pd_output, first):
    if first:
        pd_output.to_excel("output.xlsx",
                     sheet_name=employee_id, index=False)
        return

    with pd.ExcelWriter("output.xlsx",mode="a",engine="openpyxl") as writer:
        pd_output.to_excel(writer, sheet_name=employee_id,index=False)

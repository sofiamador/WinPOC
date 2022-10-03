
class Utility:
    def __init__(self, employee, task, t_now, utility_function, ro=1):

        self.xij = 0
        self.is_agent_allocated = False
        self.is_mission_allocated = False
        self.employee = employee
        self.task = task
        self.task_id = task.id_
        self.employee_id = employee.id_

        self.t_now = t_now
        self.ro = ro
        self.linear_utility = utility_function(player_entity=self.player_entity,
                                                          mission_entity=self.mission_entity,
                                                          task_entity=self.task_entity,
                                                          t_now=self.t_now)


    def update_xij_norm_r_ij(self, ratio=1):
        self.xij_normalized_times_r_ij = self.xij_normalized * self.get_utility(ratio)

    def get_utility(self, ratio=1):
        return (ratio * self.linear_utility)




class FisherSolver():
    def __init__(self ,tasks, employees):
        self.tasks = tasks
        self.employees = employees
        self.utilities = self.create_utilities()

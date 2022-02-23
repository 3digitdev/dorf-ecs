from processors.tasks.hauling import *


class TaskProcessor(Processor):
    """
    Handles assigning Tasks to Dwarves
    """
    def process(self):
        for tasker, (name, tasked) in self.world.get_components(Name, Tasked):
            priorities = [(t, p) for t, p in tasked.priorities.items()]
            priorities.sort(key=lambda x: x[1], reverse=True)
            # Sort tasks from highest to lowest priority
            for (task, _) in priorities:
                # In the loop, we look for the first task that passes the "test" for that task,
                # Meaning the task has something for the Dwarf to do.  We then assign that task.
                if task == Task.HAUL:
                    if tasked.current_task != Task.HAUL:
                        # TODO:  Somehow check that the HAUL task has anything to be done
                        tasked.current_task = Task.HAUL
                        self.world.add_component(tasker, Hauls(step=HaulStep.NEED_ITEM))
                        print(f"{name.name} task set to HAUL")
                    break
                else:  # We found no "needed" tasks, so the Dwarf goes idle.
                    tasked.current_task = Task.IDLE
                    print(f"{name.name} task set to IDLE")
                    break

import time

import pytest

from colibri.core.connectors.hydronics.fluid_flow import FluidFlowConnector

from colibri.core.models.project import Project
from colibri.models.hydronics.duct import Duct

def test_performance_linear():

    starting_time = time.perf_counter()

    n_models = 100

    project = Project()
    project.iterate = False

    # connect lots of ducts one after the other
    previous_duct = None
    liquid_flow = FluidFlowConnector()
    for d in range(n_models):
        current_duct = Duct(f"duct_{d+1}")
        if previous_duct:
            project.link(previous_duct, current_duct, liquid_flow)
        project.add(current_duct)
        previous_duct = current_duct

    project.run()
    runtime = time.perf_counter() - starting_time
    #assert runtime < 3 # this should not take more than 3 seconds
    print(f"{len(project.models)} models and {len(project.links)} links in {runtime:3.2f} seconds")

    return runtime
def performance_grid(n_models_x = 10, n_models_y = 10):

    starting_time = time.perf_counter()

    project = Project()
    project.iterate = False
    project.time_steps = 8760

    # connect lots of ducts in a grid
    liquid_flow = FluidFlowConnector()
    for x in range(2, n_models_x):
        for y in range(n_models_y):
            current_model = Duct(f"duct_{x}_{y}")
            project.add(current_model)
            right_model = project.get(f"duct_{x + 1}_{y}")
            left_model = project.get(f"duct_{x-1}_{y}")
            top_model = project.get(f"duct_{x}_{y - 1}")
            bottom_model = project.get(f"duct_{x}_{y + 1}")

            if right_model:
                project.link(current_model, right_model, liquid_flow)
            if left_model:
                project.link(current_model, left_model, liquid_flow)
            if top_model:
                project.link(current_model, top_model, liquid_flow)
            if bottom_model:
                project.link(current_model, bottom_model, liquid_flow)

    project.run()
    runtime = time.perf_counter() - starting_time
    print(f"{len(project.models)} models and {len(project.links)} links in {runtime:3.2f} seconds")

    return (runtime, len(project.links), len(project.models))

@pytest.mark.skip("Only for the report")
def test_performance_grid():
    runtime = performance_grid(10,10)[0]
    #assert runtime < 2  # this should not take more than 2 seconds

def performance_tree(n_levels = 8, backlink=True):

    starting_time = time.perf_counter()

    project = Project()
    project.iterate = False

    # connect lots of ducts in a binary tree
    root_model = Duct(f"duct_root")
    previous_ducts = [root_model]
    project.add(root_model)
    n_models = 1
    liquid_flow = FluidFlowConnector()
    for l in range(n_levels):
        current_ducts = []
        for previous_duct in previous_ducts:
            for n_son in range(2): 
                current_duct = Duct(f"duct_{n_models}")
                current_ducts.append(current_duct)
                project.link(previous_duct, current_duct, liquid_flow)
                if backlink:
                    project.link(current_duct, root_model, liquid_flow)
                project.add(current_duct)
                n_models = n_models + 1
                                
        previous_ducts = current_ducts

    project.run()

    runtime = time.perf_counter() - starting_time
    print(f"{len(project.models)} models and {len(project.links)} links in {runtime:3.2f} seconds")
    return runtime

@pytest.mark.skip("Only for the report")
def test_performance_tree():
    runtime = performance_tree(n_levels=12)
    #assert runtime < 5 # this should not take more than 5 seconds


@pytest.mark.skip("Only for the report")
def test_performance_tree_backlink():
    runtime = performance_tree(n_levels=8, backlink=True)
    #assert runtime < 5  # this should not take more than 5 seconds


@pytest.mark.skip("Only for the report")
def test_performance_grid_graph():
    runtimes = []
    n_models = []
    n_links = []
    board_size = 15
    for size in range(3, board_size):
        result = performance_grid(size, size)
        runtimes.append(result[0])
        n_links.append(result[1])
        n_models.append(result[2])

    print(runtimes)
    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twiny()
    ax1.set_xticks(n_models)
    ax1.set_xlabel("n models")
    ax2.set_xticks(n_links)
    ax2.set_xlabel("n links")

    ax1.set_ylabel("seconds")

    ax1.plot(n_models, runtimes)
    plt.show()



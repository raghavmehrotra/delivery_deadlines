import solara
from model import DeliveryModel
from mesa.visualization import (  
    SolaraViz,
    make_space_component,
    make_plot_component,
)
from mesa.visualization.components import AgentPortrayalStyle

## Define agent portrayal: color, shape, and size
def agent_portrayal(agent):
    # return AgentPortrayalStyle(
    #     color = "red" if agent.status == 1 else "blue",
    #     marker= "s",
    #     size= 75,
    # )
    pass

## Enumerate variable parameters in model:
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "rows": {
        "type": "SliderInt",
        "value": 20,
        "label": "Width",
        "min": 5,
        "max": 100,
        "step": 1,
    },
    "cols": {
        "type": "SliderInt",
        "value": 20,
        "label": "Height",
        "min": 5,
        "max": 100,
        "step": 1,
    }
}

## Instantiate model
delivery_model = DeliveryModel()

## Define happiness over time plot
# TODO: make_plot_component({"variable": "tab:green"})

## Define space component
# TODO: SpaceGraph = make_space_component(agent_portrayal, draw_grid=False)

## Instantiate page inclusing all components
# TODO:
# page = SolaraViz(
#     delivery_model,
#     components=[SpaceGraph, plot_component],
#     model_params=model_params,
#     name="Model of Quick Commerce Delivery",
# )
## Return page
# TODO: page
    

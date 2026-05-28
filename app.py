from agents import DeliveryAgent, DarkStoreAgent
from model import DeliveryModel
from mesa.visualization import SolaraViz, make_space_component, make_plot_component


def agent_portrayal(agent):
    if isinstance(agent, DarkStoreAgent):
        return {"color": "tab:blue", "marker": "s", "size": 150}
    # DeliveryAgent: red is injured, orange is active, green is idle
    if agent.is_injured:
        color = "tab:red"
    elif agent.is_idle:
        color = "tab:green"
    else:
        color = "tab:orange"
    return {"color": color, "marker": "o", "size": 40}


model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "n_workers": {
        "type": "SliderInt",
        "value": 90,
        "label": "N Workers",
        "min": 5,
        "max": 100,
        "step": 5,
    },
    "n_darkstores": {
        "type": "SliderInt",
        "value": 3,
        "label": "N Dark Stores",
        "min": 1,
        "max": 10,
        "step": 1,
    },
    "delivery_deadline": {
        "type": "SliderInt",
        "value": 20,
        "label": "Delivery Deadline (steps)",
        "min": 5,
        "max": 100,
        "step": 5,
    },
    "speed_threshold": {
        "type": "SliderFloat",
        "value": 2,
        "label": "Speed Threshold (cells/step)",
        "min": 0.5,
        "max": 4.0,
        "step": 0.1,
    },
    "cost_of_injury": {
        "type": "SliderInt",
        "value": 1000,
        "label": "Cost of Injury (INR)",
        "min": 100,
        "max": 5000,
        "step": 100,
    },
    "per_order_earnings": {
        "type": "SliderInt",
        "value": 50,
        "label": "Earnings per Order (INR)",
        "min": 10,
        "max": 200,
        "step": 10,
    },
    "injury_cooldown_duration": {
        "type": "SliderInt",
        "value": 10,
        "label": "Injury Cooldown (steps)",
        "min": 1,
        "max": 30,
        "step": 1,
    },
}

SpaceGraph = make_space_component(agent_portrayal, draw_grid=False)
InjuryCountPlot = make_plot_component({"n_injuries_total": "tab:red", "n_injured": "tab:pink"})
InjuryCostPlot = make_plot_component({"total_injury_cost": "tab:orange"})
OrdersMissedPlot = make_plot_component({"orders_missed": "tab:purple"})
AvgEarningsPlot = make_plot_component({"avg_work_earnings": "tab:green"})

model = DeliveryModel()

page = SolaraViz(
    model,
    components=[SpaceGraph, InjuryCountPlot, InjuryCostPlot, OrdersMissedPlot, AvgEarningsPlot],
    model_params=model_params,
    name="Quick Commerce Delivery ABM",
)
page

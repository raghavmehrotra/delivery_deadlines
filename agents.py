from mesa import Agent
import numpy as np

import random

class DeliveryAgent(Agent):
    # Initiate agent instance, inherit model trait from parent class
    def __init__(self, model):

        # Static variables shared across agents
        mu = 0.5
        sigma = 0.2
        low = 0
        high = 1

        super().__init__(model)
        # Draws a risk threshold for each delivery worker from a normal distribution
        self.risk_threshold = self.truncated_normal(mu, sigma, low, high)

        # Initialize all the agents to be idle at time t=0
        # Idle and working are complementary states. A worker is idle if they are 
        # not working (i.e. not waiting to pick up an order or driving to deliver it or
        # if they are injured and unable to work)
        self.is_idle = 1

        # No worker is injured at t=0
        self.is_injured = 0

        # Workers have 0 earnings at t=0
        self.work_earnings = 0

        # TODO: Draw savings from a truncated normal calibrated to urban Indian household income data
        self.savings = 0

        # Counts down from N while injured, worker cannot accept orders until it reaches 0
        self.injury_cooldown = 0

        # Set by the model when the worker is assigned an order; None when idle
        # Order is a dict: {"dark_store": <DarkStoreAgent>, "customer_pos": (x, y), "deadline": <int step>}
        self.current_order = None

        # Current movement target: dark store pos (to collect) or customer pos (to deliver)
        self.destination = None

    def truncated_normal(self, mu, sigma, low, high):
        """
        Helper function to find the normal distribution through rejection sampling
        to ensure the values are within the range.
        Reference: https://relguzman.blogspot.com/2018/04/rejection-sampling-explained.html

        Params:
            mu: distribution mean
            sigma: distribution standard deviation
            low, high: the bounds to clip the sampled number between

        Returns:
            (float) A randomly sampled real number from the distribution and within
            the bounds specified
        """
        while True:
            val = np.random.normal(mu, sigma)
            if low <= val <= high:
                return val

    def pick_move(self):
        """
        Implements the decision rule for the DeliveryAgent. [TODO: determine this]
        """

        if self.is_idle:
            pass
            # Accept or reject an order (based on earnings, risk threshold)
            # Determine a speed to drive at (based on risk threshold)

        # if not idle, they are working, so assume that they can't accept the next
        # order for now

    def step(self):
        """
        Called once per model step. Does the following:
          1. Injured: decrement injury_cooldown, change is_injured to 0 when cooldown hits 0.
          2. Idle: Agent itself doesn't do anything. The model assigns it the order.
          3. Not idle: move toward destination
        """
        pass

    def move_toward(self, destination):
        """
        Move the agent closer to destination using a Manhattan step
        on the grid.

        Params:
            destination: (x, y) tuple — the target cell on the grid.
        """
        pass
        # TODO: Figure out how this intersects with velocity. A higher velocity
        # should advance the worker more steps on the grid. Round up/down to the 
        # nearest integer to determine the number of steps?

    def calculate_required_velocity(self):
        """
        Compute the minimum average velocity needed to deliver the current
        order before the deadline.

        Returns:
            (float) Manhattan distance to destination divided by the number
            of time steps remaining until current_order["deadline"].
        """
        pass

    def resolve_accident_risk(self, velocity):
        """
        Given the worker's velocity this step, compute accident probability
        via a sigmoid on (velocity - model.speed_threshold), run a Bernoulli
        trial, and update worker state accordingly: call become_injured() if
        the trial returns a 1. Call complete_delivery() if the worker has reached
        the customer without an accident. 

        Params:
            velocity: (float) the worker's speed this step.
        """
        pass

    def complete_delivery(self):
        """
        Increment work_earnings and savings by model.per_order_earnings,
        clear current_order and destination, and set is_idle to 1.
        """
        pass

    def become_injured(self):
        """
        Mark worker as injured, start cooldown, deduct injury cost, and mark the current
        order as unfulfilled
        """
        pass


class DarkStoreAgent(Agent):

    def __init__(self, model, capacity):
        super().__init__(model)

        # Maximum number of orders the store can process simultaneously (exogenously set)
        self.capacity = capacity

        # TODO: Get lambda from literature on quick commerce order volumes in Indian cities
        self.arrival_rate = np.random.poisson(lam=5)

        # Active orders currently being fulfilled by workers; each entry is:
        # {"customer_pos": (x, y), "deadline": <int step>, "worker": <DeliveryAgent or None>}
        self.queue = []

        # Orders that arrived when queue was at capacity. Cleared when the dark store can
        # fulfill more orders
        self.waiting_list = []

    def step(self):
        """
        Called once per model step. Does two things:
          1. Generate new orders this step via a Poisson draw on arrival_rate.
             Add each new order to the queue if below capacity, else to waiting_list.
          2. Promote orders from waiting_list into the queue to fill any
             slots freed up by workers who collected their orders this step.
        """
        # TODO: Apply a time-of-day multiplier to arrival_rate to capture morning/evening demand peaks

        # Generate new orders
        # n_new_orders = Poisson draw using self.arrival_rate
        # For each new order:
        #   Build an order dict with customer_pos (random cell on grid), deadline (model.steps + model.delivery_deadline), worker=None
        #   If there is space in the queue: append to queue
        #   Else: append to waiting_list

        # Promote from waiting_list to fill open queue slots
        # While len(self.queue) < self.capacity and self.waiting_list is not empty:
        #   Pop the first item from waiting_list and append it to queue
        pass

    def assign_order(self, worker):
        """
        Assign the first queued order to the given worker. Sets the order's
        worker field, sets worker.current_order and worker.destination to the
        dark store's position (worker must travel here first to collect), and
        sets worker.is_idle to 0.

        Params:
            worker: DeliveryAgent — an idle worker to assign the order to.
        """
        # Pop the first order from self.queue
        # order["worker"] = worker
        # worker.current_order = order
        # worker.destination = self.pos (worker heads to dark store first)
        # worker.is_idle = 0
        pass

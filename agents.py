from mesa import Agent
import numpy as np
import math

class DeliveryAgent(Agent):
    # Initiate agent instance, inherit model trait from parent class
    def __init__(self, model):

        super().__init__(model)

        # Initialize all the agents to be idle at time t=0
        # Idle and working are complementary states. A worker is idle if they are 
        # not working (i.e. not waiting to pick up an order or driving to deliver it or
        # if they are injured and unable to work)
        self.is_idle = 1

        # No worker is injured at t=0
        self.is_injured = 0

        # Workers have 0 earnings at t=0
        self.work_earnings = 0

        # From monthly per capita expditure (MPCE) using National Sample Survey data for
        # families in urban Karnataka (capital Bangalore). Assumes 5% savings per month
        # and that the delivery worker comes in with 6 months of savings.
        # Mean is the average 6 months savings at 5% using the 60, 70 and 80th
        # percentile MPCE from NSS data. std dev is 0.3 of the mean, high is 2 std
        # devs away from the mean. See attached paper for details.
        self.savings = self.truncated_normal(mu=44188, sigma=13256, low=0, high=70701)

        # Calculates a risk threshold for each delivery worker as a function of
        # their savings. High savings mean less likely to take risks, and vice versa.
        self.risk_threshold = self.calculate_risk(self.savings, 0, 70701)

        # Counts down from 5 while injured, worker cannot accept orders until it reaches 0
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
            val = self.random.gauss(mu, sigma)
            if low <= val <= high:
                return val

    def calculate_risk(self, savings, low, high, k=10):
        """
        Applies a normalized sigmoid function to the worker's savings to
        calculate their risk threshold. In general, higher prior savings means
        the worker is less willing to take risks (and vice versa)

        Params:
            savings (int): Worker savings drawn from a normal distribution
            low (int): global lower bound on savings
            high (int): global upper bound on savings
            k (int): scaling parameter for sigmoid to determine how flat
                     the mapping is. Default of 10 to make the relationship
                     steeper
        Returns:
            A normalized risk score between 0 and 1

        """
        savings_norm = (savings - low) / high
        # Subtracting 0.5 to ensure that the sigmoid is 0 centered.
        # Source: https://deepai.org/machine-learning-glossary-and-terms/sigmoidal-nonlinearity
        # and Gemini conversation around the formula.
        sigmoid = 1 / (1 + np.exp(-k * (savings_norm - 0.5)))

        # To model the inverse relationship
        return 1 - sigmoid

    def calculate_actual_velocity(self):
        """
        Returns the velocity the agent will drive at, blending the
        safe baseline (safe_speed) and the deadline-required speed,
        weighted by the agent's risk_threshold.
        """

        required = self.calculate_required_velocity()
        # The logic here is to weigh the actual velocity the worker chooses
        # by the risk_threshold.
        # We use the initial risk_threshold instead of dynamically calculating it
        # for simplicity. A worker's risk_threshold does not evolve over time.
        return (1 - self.risk_threshold) * self.model.safe_speed \
             + self.risk_threshold * required


    def step(self):
        """
        Called once per model step. Follows logic based on one of three states
        that the worker can be in: injured, idle, active
        """
        if self.is_injured:
            self.injury_cooldown -= 1
            if self.injury_cooldown == 0:
                self.is_injured = 0

        # Worker is not injured AND active. We don't do anything if the worker
        # is idle. The model assigns orders to such workers
        elif not self.is_idle:
            # The model has reached the step number that exceeds the step number
            # by which the worker should have reached the destination, i.e. the 
            # order was not fulfilled.
            if self.model.steps >= self.current_order["deadline"]:
                self.model.orders_missed += 1
                self.current_order = None
                self.destination = None
                self.is_idle = 1
                return

            # Order can still be fulfilled
            velocity = self.calculate_actual_velocity()
            self.resolve_accident_risk(velocity)

            if not self.is_injured:
                # Velocity is a real number, so we round this. e.g. if velocity
                # is 1.6, n_steps is 2 and the worker can cover two squares in the
                # direction of the destination. This overestimates how fast the worker
                # goes, but is necessary with the current design.
                n_steps = max(1, round(velocity))
                for _ in range(n_steps):
                    if self.pos == self.destination:
                        break
                    self.move_toward(self.destination)

                if self.pos == self.destination:
                    if self.destination == self.current_order["dark_store"].pos:
                        # Arrived at dark store — switch to delivery leg
                        self.destination = self.current_order["customer_pos"]
                    else:
                        # Arrived at customer
                        self.complete_delivery()

    def move_toward(self, destination):
        """
        Move the agent closer to destination using a Manhattan step
        on the grid. Called up to round(velocity) times per tick from step().

        Params:
            destination: (x, y) tuple — the target cell on the grid.
        """
        # Uses the Manhattan distance to calculate how many horizontal and vertical
        # moves are required
        dx = destination[0] - self.pos[0]
        dy = destination[1] - self.pos[1]

        # Prioritize horizontal moves over vertical ones - this is arbitrary
        if dx != 0:
            new_pos = (self.pos[0] + (1 if dx > 0 else -1), self.pos[1])
        else:
            new_pos = (self.pos[0], self.pos[1] + (1 if dy > 0 else -1))
        self.model.grid.move_agent(self, new_pos)

    def calculate_required_velocity(self):
        """
        Compute the minimum average velocity needed to deliver the current
        order before the deadline.

        Returns:
            (float) Manhattan distance to destination divided by the number
            of time steps remaining until current_order["deadline"].
        """
        dist = abs(self.destination[0] - self.pos[0]) + abs(self.destination[1] - self.pos[1])

        # The deadline is calculated as the global 'turn' or 'step' number of
        # the model. So the difference is the number of steps left, within which
        # the worker must make it to the destination
        steps_remaining = self.current_order["deadline"] - self.model.steps
        if steps_remaining <= 0:
            # It is impossible to reach the destination
            return float('inf')
        
        return dist / steps_remaining

    def resolve_accident_risk(self, velocity, k=5, offset=1):
        """
        Given the worker's velocity this step, compute accident probability
        via a sigmoid on (velocity - model.speed_threshold), run a Bernoulli
        trial, and update worker state accordingly: call become_injured() if
        the trial returns a 1.

        Params:
            velocity: (float) the worker's speed this step.
            k: (int) parameter determining the steepness of the sigmoid function
            offset: (int) moves the sigmoid center (p=0.5) to a threshold of 2.5.
                The risk builds up gradually post 1.5 (45 km/hr) rather than being
                0.5 exactly at the threshold
            
        """

        # Similarly to the calculate_risk, this uses a normalized sigmoid
        # to calculate the probability of accident.
        exponent = -k * (velocity - (self.model.speed_threshold + offset))
        p = 1.0 / (1.0 + math.exp(exponent))
        if self.random.random() < p:
            self.become_injured()

    def complete_delivery(self):
        """
        Increment work_earnings and savings by model.per_order_earnings,
        clear current_order and destination, and set is_idle to 1.
        """

        # Increment worker earnings and model params
        self.work_earnings += self.model.per_order_earnings
        self.savings += self.model.per_order_earnings
        self.model.orders_fulfilled += 1
        
        # Worker is ready to accept a new order
        self.current_order = None
        self.destination = None
        self.is_idle = 1

    def become_injured(self):
        """
        Mark worker as injured, start cooldown, deduct injury cost, and mark the current
        order as unfulfilled
        """

        # Worker suffers a fixed cost and can no longer accept new orders
        self.is_injured = 1
        self.injury_cooldown = self.model.injury_cooldown_duration
        self.savings -= self.model.cost_of_injury
        self.current_order = None
        self.destination = None
        self.is_idle = 1
        
        # Increment model params
        self.model.orders_missed += 1
        self.model.total_injury_cost += self.model.cost_of_injury
        self.model.n_injuries_total += 1
        


class DarkStoreAgent(Agent):

    def __init__(self, model, capacity):
        super().__init__(model)

        # Maximum number of orders the store can process simultaneously (exogenously set)
        self.capacity = capacity

        # Arrival rate calibration (1 step = 1 minute):
        # Source: https://cmr.berkeley.edu/2026/01/the-dark-store-revolution-how-indias-10-minute-economy-is-redefining-retail-infrastructure/).
        # See attached paper for calculations (in summary: 1800 orders per day, 
        # stores open 16 hours.= 960 minutes. Arrival uniform at 1800/960 per step)
        self.arrival_rate = 1.875

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
        
        # Runs a Poisson draw for number of orders in this step
        n_new = np.random.poisson(self.arrival_rate)
        for _ in range(n_new):
            order = {
                "dark_store": self,
                "customer_pos": self.random.choice(self.customer_locations),
                "deadline": None, # assigned only when the worker begins driving to store
                "worker": None,
            }
            if len(self.queue) < self.capacity:
                self.queue.append(order)
            else:
                self.waiting_list.append(order)

        # AI: Used Claude Code to find this missing piece -- it was important
        # to empty the waiting list to account for orders fulfilled in the previous
        # round.
        while len(self.queue) < self.capacity and self.waiting_list:
            self.queue.append(self.waiting_list.pop(0))

    def assign_order(self, worker):
        """
        Assign the first queued order to the given worker. Updates the relevant
        fields.

        Params:
            worker: DeliveryAgent — an idle worker to assign the order to.
        """
        order = self.queue.pop(0)
        order["worker"] = worker
        order["deadline"] = self.model.steps + self.model.delivery_deadline
        worker.current_order = order
        # Worker travels to dark store first to collect
        worker.destination = self.pos
        worker.is_idle = 0

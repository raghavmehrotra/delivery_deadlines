from mesa import Model
from mesa.space import MultiGrid
from agents import DeliveryAgent, DarkStoreAgent
from mesa.datacollection import DataCollector

class DeliveryModel(Model):
    """
    Scale: 1 step = 1 minute, 1 cell = 0.5 km → grid is 10 km x 10 km

    A delivery deadline of 20 min is 20 steps
    A safe speed of 45 km/hr is 90 cells/60 steps = 1.5 cells/step
    Similarly, 60 km/hr is 2 cells/step
    """

    def __init__(
        self,
        seed=42,
        width=20,
        height=20,
        n_workers=90,
        n_darkstores=3,
        dark_store_capacity=10,
        delivery_deadline=20,
        safe_speed=1.5,
        speed_threshold=2,
        cost_of_injury=2000,
        per_order_earnings=50,
        injury_cooldown_duration=5,
    ):
        if seed is not None:
            seed = int(seed)
        super().__init__(rng=seed)

        self.width = width
        self.height = height
        self.n_workers = n_workers
        self.n_darkstores = n_darkstores
        self.delivery_deadline = delivery_deadline
        self.safe_speed = safe_speed
        self.speed_threshold = speed_threshold
        self.cost_of_injury = cost_of_injury
        self.per_order_earnings = per_order_earnings
        self.injury_cooldown_duration = injury_cooldown_duration

        # Counters updated by agents each step; read by the DataCollector
        self.orders_fulfilled = 0
        self.orders_missed = 0
        self.total_injury_cost = 0
        self.n_injuries_total = 0

        self.grid = MultiGrid(width, height, torus=False)

        # Three dark stores at fixed positions forming a triangle across the grid,
        # trying to minimize the overlap.
        # Grid is 20x20 (10km x 10km):
        #   (5,5) = SW neighborhood (2.5km, 2.5km)
        #   (15,5) = SE neighborhood (7.5km, 2.5km)
        #   (10,15)= N neighborhood (5km, 7.5km)
        neighborhood_positions = [(5, 5), (15, 5), (10, 15)]
        for pos in neighborhood_positions[:n_darkstores]:
            store = DarkStoreAgent(self, capacity=dark_store_capacity)
            self.grid.place_agent(store, pos)
            # Generate 50 household positions clustered around each store at a distance of 2km (so 4 cells).
            # Orders sample from this fixed pool, so deliveries go to realistic recurring locations.
            store.customer_locations = [
                (
                    # AI prompt: "How do I sample and assign 50 locations in a MultiGrid
                    # that are 2km or 4 cells away from fixed locations on the grid."
                    int(min(max(round(self.random.normalvariate(pos[0], 4)), 0), width - 1)),
                    int(min(max(round(self.random.normalvariate(pos[1], 4)), 0), height - 1)),
                )
                for _ in range(50)
            ]

        # Place delivery workers at random positions on the grid. This mimics the
        # fact that they often do not live near stores and are constantly mobile.
        for _ in range(n_workers):
            worker = DeliveryAgent(self)
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            self.grid.place_agent(worker, (x, y))

        self.datacollector = DataCollector(
            model_reporters={
                "orders_fulfilled": "orders_fulfilled",
                "orders_missed": "orders_missed",
                "n_injured": lambda m: sum(1 for a in m.agents if isinstance(a, DeliveryAgent) and a.is_injured),
                "total_injury_cost": "total_injury_cost",
                "n_injuries_total": "n_injuries_total",
                "avg_work_earnings": lambda m: (
                    sum(a.work_earnings for a in m.agents if isinstance(a, DeliveryAgent)) / m.n_workers
                ),
                "avg_savings": lambda m: (
                    sum(a.savings for a in m.agents if isinstance(a, DeliveryAgent)) / m.n_workers
                ),
            }
        )

        self.datacollector.collect(self)

    def step(self):
        """
        Defines a step in the model.
        """
        super().step()
        # First generate the orders for this time step
        self.agents_by_type[DarkStoreAgent].do("step")
        self._assign_workers_to_orders()
        # Workers activate in a random order each step to avoid bias
        self.agents_by_type[DeliveryAgent].shuffle_do("step")
        self.datacollector.collect(self)

    def _assign_workers_to_orders(self):
        """
        For each dark store with queued orders, assign the nearest idle
        (and uninjured) worker until either the queue or idle pool is exhausted.
        """
        idle_workers = [
            a for a in self.agents_by_type[DeliveryAgent]
            if a.is_idle and not a.is_injured
        ]
        for store in self.agents_by_type[DarkStoreAgent]:
            while store.queue and idle_workers:
                nearest = min(
                    idle_workers,
                    key=lambda w: abs(w.pos[0] - store.pos[0]) + abs(w.pos[1] - store.pos[1])
                )
                store.assign_order(nearest)
                idle_workers.remove(nearest)
        
        

    
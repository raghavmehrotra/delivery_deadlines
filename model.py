from mesa import Model
from mesa.space import MultiGrid
from agents import DeliveryAgent, DarkStoreAgent
from mesa.datacollection import DataCollector

class DeliveryModel(Model):

    def __init__(
        self,
        seed=42,
        width=20,
        height=20,
        n_workers=30,
        n_darkstores=3,
        dark_store_capacity=10,
        delivery_deadline=20,
        speed_threshold=1.5,
        cost_of_injury=500,
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
        self.speed_threshold = speed_threshold
        self.cost_of_injury = cost_of_injury
        self.per_order_earnings = per_order_earnings
        self.injury_cooldown_duration = injury_cooldown_duration

        # Counters updated by agents each step; read by the DataCollector
        self.orders_fulfilled = 0
        self.orders_missed = 0
        self.total_injury_cost = 0

        self.grid = MultiGrid(width, height, torus=False)

        # TODO: Choose fixed neighborhood positions for dark stores rather than random placement
        # One dark store per neighborhood. Placing them randomly for now, look at literature
        for _ in range(n_darkstores):
            store = DarkStoreAgent(self, capacity=dark_store_capacity)
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            self.grid.place_agent(store, (x, y))


        # TODO: Update locations of customers/homes on the map according to data/literature.
        # These will likely be clustered around the dark stores.

        # Place delivery workers at random positions on the grid.
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
        pass
        
        

    
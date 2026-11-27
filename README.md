# Robotic Device-Testing Line: A SimPy Digital Twin

A discrete-event simulation of a smart-factory testing line, built for **SSW 325**. Devices such as phones and tablets arrive, get charged, get tested, and finish, and a single robotic arm carries them between stations. The goal is to find what limits **throughput** (devices tested per hour) while respecting station capacity, arm motion time, and the rule that a device must be fully charged before it is tested.

Built with **Python** and **[SimPy](https://simpy.readthedocs.io/)**.

---

## How the factory works

```
 Idle Rack  ──arm──▶  Charging Area  ──arm──▶  Testing Lab  ──arm──▶  Done Rack
 (unlimited)          24 ports C1–C24          20 benches T(1-1)–T(4-5)   (unlimited)
                      ~30 min (exponential)    ~20 min (exponential)
```

1. **Arrival:** a new device enters the Idle Rack (every 1 minute by default).
2. **Charging assignment:** the controller reserves a free charger.
3. **Move to charging:** the robotic arm carries the device from the Idle Rack to the charger.
4. **Charging:** random time, exponentially distributed with a mean of 30 minutes.
5. **Testing assignment:** once the device is fully charged, the controller reserves a free test bench. The device keeps its charger busy until a bench is free.
6. **Move to testing:** the arm carries the device from the charger to the bench.
7. **Testing:** random time, exponentially distributed with a mean of 20 minutes, with a 95% pass rate.
8. **Completion:** the arm carries the device to the Done Rack.

### Robotic arm

- A single arm modeled as a `simpy.Resource` with capacity 1, so moves queue up while it's busy.
- Each move is an explicit `MoveCommand`, for example `Move C5 -> T(1-1)`.
- The arm tracks its position. A move first travels empty from where the arm is to the source, then carries the device to the destination.
- **Travel time** = Manhattan distance × base travel rate (0.2 min per grid unit) × random factor of 0.95–1.05.
- **Arm utilization** = busy time ÷ total simulation time.

### Floor layout (grid units)

| Area | Position |
|---|---|
| Idle Rack | (0, 0) |
| Chargers C1–C24 | Rows of 6 starting at (2, 0): C1 = (2, 0) … C24 = (7, 3) |
| Test benches T(1-1)–T(4-5) | 4 × 5 grid starting at (2, 5): T(1-1) = (2, 5) … T(4-5) = (6, 8) |
| Done Rack | (0, 9) |

---

## Project structure

| File | Contents |
|---|---|
| `main.py` | Runs one 8-hour shift and prints the results |
| `experiments.py` | Changes one setting at a time, averages 5 seeds per setting, and saves a CSV and a chart |
| `factory_controller.py` | `FactoryController`: arrivals, charger and bench assignment, the `can_test()` safety rule, arm commands, statistics |
| `robotic_arm.py` | `RoboticArm`: travel time, `pick`, `place`, `execute(cmd)`, utilization |
| `move_command.py` | `MoveCommand`: one move order with issued, started and completed times |
| `charging_station.py` | `ChargingStation`: reserve → load → charge → unload, with state and utilization |
| `test_branch.py` | `TestStation`: reserve → load → test → unload, with pass/fail result and utilization |
| `idle_rack.py` | `IdleRack`: unlimited arrival buffer (`simpy.Store`) |
| `done_rack.py` | `DoneRack`: unlimited buffer for finished devices |
| `device.py` | `Device`: state, battery level, location, timestamps, `is_fully_charged()`, `cycle_time()` |
| `SSW325_Factory_Sim_Presentation.pptx` | 6-slide project presentation |
| `Video_Script.md` | Script for the video presentation |

### UML

- [Class diagram](Screenshot%202026-11-17%20174655.png)
- [Sequence diagram: Arrival → Charging → Testing → Done](Screenshot%202026-11-17%20175616.png)

---

## Getting started

**Requirements:** Python 3.9 or newer.

```bash
git clone https://github.com/CLUJMAN/ssw325-factory-sim.git
cd ssw325-factory-sim
pip install -r requirements.txt
```

**Run one shift:**

```bash
python main.py
```

**Run the experiments:**

```bash
python experiments.py
```

This writes `experiment_results.csv`, and `experiment_results.png` if matplotlib is installed.

### Changing the configuration

Every major setting is a parameter of `FactoryController`:

```python
fc = FactoryController(
    env,
    num_chargers=24,        # charging ports
    num_benches=20,         # test benches (laid out 5 per row)
    arrival_interval=1,     # minutes between new devices
    base_travel_rate=0.2,   # arm minutes per grid unit
    mean_charge_time=30,    # minutes
    mean_test_time=20,      # minutes
)
```

---

## Results

### Baseline: one 8-hour shift (seed 42)

| Metric | Value |
|---|---|
| Devices tested | 61 (58 passed) |
| Throughput | 7.6 devices/hour |
| Average cycle time | 233 minutes |
| Arm utilization | 99.4% |
| Charger utilization | 26.9% |
| Test bench utilization | 26.0% |
| Safety violations | 0 |

### Experiments (averaged over 5 seeds)

| Setting changed | Range | Throughput (devices/hour) |
|---|---|---|
| Arm travel rate (min per grid unit) | 0.30 → 0.05 | 4.8 → 28.0 |
| Number of chargers | 12 → 36 | 7.3 → 7.4 |
| Number of test benches | 10 → 30 | ≈ 7.4 throughout |
| Arrival interval (min) | 1 → 5 | 7.4 → 6.9 |

### Takeaway

The single robotic arm is the bottleneck. It is busy about 99% of the time, while chargers and benches sit idle about three quarters of the time. Making the arm twice as fast roughly doubles throughput, but adding chargers or benches does almost nothing. The best ways to improve this factory are a **second arm** or **smarter move ordering**, such as prioritizing moves that free a charger or bench, not more stations.

---

## Possible extensions

- Multiple robotic arms
- Move prioritization and scheduling strategies
- Collision avoidance between arms
- Larger or rearranged floor layouts

# Video Presentation Script: Robotic Device-Testing Line

**Total length:** about 6–7 minutes (roughly 1 minute per slide)
**Tip:** Lines in *[brackets]* are cues for you. Don't read them out loud.

---

## Slide 1: Title (about 30 seconds)

*[Title slide on screen]*

Hi, my name is ______, and this is my SSW 325 project: a digital twin of a robotic device-testing line.

In modern electronics factories, devices like phones and tablets have to be charged and tested before they ship, and a robotic arm moves them between stations. For this project, I modeled that system in UML and then simulated it in Python using SimPy. The main goal was to find out what limits **throughput**, which is the number of devices tested per hour.

---

## Slide 2: The Four-Stop Path (about 1 minute)

*[Point to each card from left to right]*

Every device follows the same four-stop path.

First, it arrives at the **Idle Rack**. In my simulation, a new device arrives every minute, and the rack can hold an unlimited number of devices.

Next, the controller finds a free spot in the **Charging Area**. There are 24 charging ports, labeled C1 through C24. Charging takes a random amount of time, exponentially distributed with a mean of 30 minutes.

When charging is done, the device goes to the **Testing Lab**, which has 20 test benches arranged in a 4-by-5 grid. Testing averages 20 minutes, and about 95 percent of devices pass.

Finally, the device goes to the **Done Rack**.

The little arrows between the cards are important. Every one of those moves is done by the robotic arm, and every move takes real travel time.

*[Point to the safety rule at the bottom]*

There's also a safety rule: a device can only go to a test bench once it's fully charged. If every bench is busy, the device just waits on its charger, which keeps that charger busy too.

---

## Slide 3: Class Design (about 1 minute)

*[Point to the left column, then the right]*

The code is built from eight classes that match my UML class diagram. I split them into two groups.

On the left are the classes that handle **control and motion**. The **FactoryController** is the brain. It handles arrivals, assigns chargers and test benches, enforces the fully-charged rule, and collects statistics. It never moves a device itself. Instead, it creates a **MoveCommand**, like "Move C5 to T(1-1)", and sends it to the **RoboticArm**.

On the right are the **physical resources**: the Idle Rack and Done Rack, the Charging Stations, the Test Stations, and the Device itself. Each station only knows whether it's free and how long its work takes. Each device keeps track of its own state, battery level, location, and timestamps.

Keeping control separate from the physical resources made it easy to change things like the number of chargers or benches when I ran experiments.

---

## Slide 4: The Robotic Arm (about 1 minute)

*[Point to the numbered steps]*

The robotic arm is what turns every move into real time. Each move follows four steps.

One: wait for the arm. The arm is a SimPy resource with a capacity of one, so it can only do one move at a time, and any other moves wait in line.

Two: travel to the source and pick up the device. Picking a device up frees the charger or bench it was on.

Three: carry it to the destination and place it there.

Four: log the move, so I can measure how busy the arm was.

*[Point to the formula, then the floor map]*

Travel time is based on the Manhattan distance between two spots on the factory floor grid, shown on the right. I multiply that distance by 0.2 minutes per grid unit, plus or minus 5 percent random variation. The arm also has to travel back empty from wherever it finished its last move, which adds up quickly.

---

## Slide 5: Baseline Results (about 1 minute)

*[Point to the four numbers, then the chart]*

Here are the results from one 8-hour shift.

61 devices finished testing, which is about 7.6 devices per hour. The average device spent about 233 minutes in the factory from arrival to finish. And there were zero safety violations, so no device was ever tested before it was fully charged.

The chart on the right is the most important result. The robotic arm was busy 99.4 percent of the time. The chargers and test benches, on the other hand, were only busy about 26 percent of the time.

That means the stations spend most of their time waiting for the arm. The arm is the bottleneck, and most of that 233-minute cycle time is devices waiting for a move.

---

## Slide 6: Experiments and Conclusion (about 1 minute 15 seconds)

*[Point to the chart, then the cards on the right]*

To confirm the bottleneck, I ran experiments that changed one setting at a time, averaging each one over five runs with different random seeds.

The chart shows what happens when I change the arm's speed. When the arm takes 0.05 minutes per grid unit, throughput is 28 devices per hour. At 0.3 minutes, it drops to under 5. In short, a twice-as-fast arm gives roughly twice the throughput.

But adding stations barely helps at all. Going from 12 chargers to 36 only moved throughput from 7.3 to 7.4 devices per hour, and changing the number of test benches from 10 to 30 had almost no effect.

*[Point to Next steps]*

So my conclusion is that to improve this factory, you should invest in arm capacity, not more stations. The next steps would be adding a second arm, or prioritizing the moves that free up a charger or bench first.

Thanks for watching.

---

## Before you record

- Fill in your name on Slide 1.
- If you worked in a group, change "I" and "my" to "we" and "our".
- Practice once with a timer. If you run long, Slides 3 and 4 are the easiest to shorten.

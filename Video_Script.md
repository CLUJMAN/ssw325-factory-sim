# Video Presentation Script: Robotic Device-Testing Line

**Total length:** about 6–7 minutes (roughly 1 minute per slide)
**Tip:** Lines in *[brackets]* are cues for you. Don't read them out loud.

---

## Slide 1: Title (about 30 seconds)

*[Title slide on screen]*

Hey everyone, I'm ______, and this is my SSW 325 project. Basically, I built a digital twin of a robotic device-testing line.

So the idea is, in electronics factories, stuff like phones and tablets has to get charged and tested before it ships, and there's a robotic arm moving everything around between stations. I modeled that in UML, and then I simulated it in Python with SimPy. The big question I wanted to answer was: what's actually slowing down throughput? And by throughput, I just mean how many devices get tested per hour.

---

## Slide 2: The Four-Stop Path (about 1 minute)

*[Point to each card from left to right]*

So every device goes through the same four stops.

First, it shows up at the **Idle Rack**. In my sim, a new device comes in every minute, and the rack doesn't have a limit, so it can hold as many as it needs to.

Then the controller looks for an open spot in the **Charging Area**. There are 24 chargers, C1 through C24. Charging time is random. It's exponentially distributed with an average of 30 minutes.

Once it's charged, it heads to the **Testing Lab**, which has 20 test benches set up in a 4-by-5 grid. Testing takes about 20 minutes on average, and around 95 percent of devices pass.

And last, it ends up on the **Done Rack**.

One thing I want to point out is these little arrows between the cards. Every single one of those is the robotic arm physically moving the device, and every move takes actual time. That ends up being a really big deal later.

*[Point to the safety rule at the bottom]*

There's also a safety rule: a device can't get tested until it's fully charged. And if all the benches are full, the device just sits on its charger and waits, which means that charger is stuck being busy too.

---

## Slide 3: Class Design (about 1 minute)

*[Point to the left column, then the right]*

For the code, I've got eight classes, and they line up with my UML class diagram. I kind of split them into two groups.

On the left is the **control and motion** side. The **FactoryController** is pretty much the brain of the whole thing. It handles new arrivals, picks which charger or test bench a device goes to, makes sure the fully-charged rule is followed, and keeps track of all the stats. But it never actually moves anything itself. Instead, it makes a **MoveCommand**, something like "Move C5 to T(1-1)", and hands it off to the **RoboticArm**.

On the right is the **physical** side: the Idle Rack and Done Rack, the Charging Stations, the Test Stations, and the Device itself. The stations are pretty simple. They just know if they're free and how long their job takes. And each device keeps track of its own stuff, like its state, battery level, where it is, and timestamps for everything.

Splitting it up like this was really helpful, because when I ran experiments, I could just change the number of chargers or benches without rewriting anything.

---

## Slide 4: The Robotic Arm (about 1 minute)

*[Point to the numbered steps]*

Okay, so the robotic arm is what makes every move actually take time. Every move goes through four steps.

Step one, it waits for the arm. The arm is a SimPy resource with a capacity of one, so it can only do one thing at a time. If it's busy, every other move just waits in line.

Step two, the arm goes to wherever the device is and picks it up, which frees up that charger or bench.

Step three, it carries the device over to where it's going and drops it off.

And step four, it logs the move so I can figure out how busy the arm was.

*[Point to the formula, then the floor map]*

For travel time, I used the Manhattan distance between spots on the factory floor, which is the grid on the right. I multiply that by 0.2 minutes per grid square, and then add a little randomness, plus or minus 5 percent. Also, the arm has to drive back empty from wherever it finished its last move, and that adds up a lot faster than you'd think.

---

## Slide 5: Baseline Results (about 1 minute)

*[Point to the four numbers, then the chart]*

Alright, so here's what happened over one 8-hour shift.

61 devices made it all the way through testing, which works out to about 7.6 per hour. On average, a device spent around 233 minutes in the factory from start to finish. And there were zero safety violations, so nothing ever got tested before it was fully charged, which is good.

But honestly, the chart on the right is the main thing to look at. The robotic arm was busy 99.4 percent of the time. Meanwhile, the chargers and test benches were only busy about 26 percent of the time.

So basically, the stations are just sitting around waiting for the arm. The arm is the bottleneck, and most of that 233 minutes is devices waiting to get moved.

---

## Slide 6: Experiments and Conclusion (about 1 minute 15 seconds)

*[Point to the chart, then the cards on the right]*

To make sure the arm really was the problem, I ran some experiments where I changed one thing at a time, and I averaged each one over five runs with different random seeds.

This chart shows what happens when you change how fast the arm is. When it takes 0.05 minutes per grid square, you get 28 devices per hour. But at 0.3, it drops to less than 5. So pretty much, if the arm is twice as fast, you get about twice the throughput.

Adding more stations, though, barely did anything. Going from 12 chargers all the way up to 36 only moved throughput from 7.3 to 7.4 per hour. And changing the number of test benches from 10 to 30 basically did nothing.

*[Point to Next steps]*

So my takeaway is, if you want this factory to get more done, you need to put money into the arm, not into more stations. If I kept working on this, I'd try adding a second arm, or making the arm prioritize moves that free up a charger or bench first.

That's it for my project. Thanks for watching!

---

## Before you record

- Fill in your name on Slide 1.
- If you worked in a group, change "I" and "my" to "we" and "our".
- Practice once with a timer. If you run long, Slides 3 and 4 are the easiest to shorten.

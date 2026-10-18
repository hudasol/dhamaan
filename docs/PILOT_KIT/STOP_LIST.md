# Stop list: conditions under which a test must not proceed

**Status: proposal.** If any condition below holds, the test does not start, or stops at once and the robot is made safe. Record which condition and when on the bench sheet. These are practical rules for a pilot, not requirements of any standard.

## People and the test area

- A person who is not part of the test is inside the test area, or the area cannot be closed.
- The safety observer is absent, or the test lead is working alone.
- The emergency stop has not been checked on the day, or it did not stop the robot when checked.
- Anyone involved has not read this list and the bench sheet.

## The robot

- Any component is at or above its limit in the limit register, or the limit register for the day is missing.
- The air temperature is above the robot's rated ambient as stated by its maker, unless the test is a planned soak in a chamber with its own stop rules.
- The battery shows swelling, damage, leaks, unusual heat or a fault code.
- A sensor window is cracked, or a contamination is applied that is not documented by material, amount and method.
- The software version differs from the one named in the preregistration.

## Site and weather

- A weather or dust warning is in force for the site, or wind, sand or rain makes the area unsafe for people.
- Lighting or glare conditions make it unsafe for people to see the robot.
- A route crosses a public road, unless the regime for that has been determined and the needed permission is held.

## GNSS

- Any plan involves generating, transmitting, recording or simulating GNSS signals at the radio level. Out of scope, always.
- A fault is to be injected anywhere other than into a copy of a logged position stream in software.

## Data

- Cameras would record identifiable people and no privacy review has been done; log saturation values only.
- The log clock is not shared by every stream, or the log folder for the run cannot be identified.

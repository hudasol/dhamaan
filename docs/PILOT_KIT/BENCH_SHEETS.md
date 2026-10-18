# Bench test sheets: dust, glare and heat

**Status: proposal.** Print one sheet per run. Values that are blank are filled by the test lead on the day; nothing on these sheets is a requirement of any standard. Fix the acceptance values in a preregistration before the first run, as the repository did for its simulations. Read `STOP_LIST.md` before starting.

## Common header (every sheet)

| Field | Entry |
|---|---|
| Run label and date | |
| Robot or sensor head (model, serial) | |
| Software version | |
| Site and test area | |
| Test lead and safety observer | |
| Preregistration file and its SHA-256 | |
| Log folder name | |
| Stop list read and confirmed (initials) | |

## Sheet DU4: dirty window check (dust)

| Step | Action | Record |
|---|---|---|
| a | Photograph the clean sensor window | Photo file name |
| b | Run the obstacle approach with the clean window | Detection distance; stop distance; log folder |
| c | Apply the documented contamination (material, amount, method) | Description; photo file name |
| d | Repeat the obstacle approach | Detection distance; stop distance; valid return ratio range |
| e | Check that the monitor reports reduced sensing (DU5) | Time from contamination run start to monitor action |
| f | Clean the window and repeat step b | Detection distance |
| g | Compare the direction of the result with the simulated sweep DU3 (AC-DU3) | Agree or disagree; if disagree, DU3 is not used as evidence |

## Sheet GL2: glare route log

| Step | Action | Record |
|---|---|---|
| a | Take the route and times from the glare map (GL1) | Route name; planned time; computed sun elevation and azimuth |
| b | Drive the route at the planned time with logging on | Log folder; saturation range; any slow command |
| c | Place the standard obstacle at the marked point and approach | Detected (yes or no); distance |
| d | Note blinds, film and floor state | Description |
| e | Check the response (GL5): slow down or stop when glare degrades sensing | Time from saturation above threshold to the command |

## Sheet H4 and H5: safety function at heat soak and limit response

| Step | Action | Record |
|---|---|---|
| a | Record the component limit register (H2) used today | Limit per component and its source page |
| b | Record the reference stopping distance and response time at normal temperature | Values; log folder |
| c | Soak the robot in the planned condition (chamber or a hot day, labelled bench or field) | Start and end time; ambient; component temperatures |
| d | Repeat the stopping test at soak | Values; log folder |
| e | Run the mission profile and watch for derate or park before any limit (H5) | Time and temperature at the first derate; margin to each limit |
| f | Restart after a sun soak (H6), if planned | Time to first move; component temperatures at start |
| g | Compare the prediction filed before the test (H3) with the measurement | Difference per component |

## Sign off

| Field | Entry |
|---|---|
| Any stop list condition met during the run (which, when) | |
| Deviations from the preregistration | |
| Test lead signature | |
| Safety observer signature | |

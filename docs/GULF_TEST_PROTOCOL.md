# Gulf Test Protocol: heat, dust, glare and GNSS degradation

**Status: proposal. Nothing in this document is a result.** No test described here has been run. No claim of certification, compliance or endorsement by any authority is made or implied.

## 1. Purpose and scope

The evidence table (`data/evidence_table.csv`) was searched (before the second verification, and checked again after it) for any instrument that requires a robot to be tested against Gulf heat, dust, glare, or GNSS jamming or spoofing. None was found. This protocol proposes what a developer could test anyway, and how the results could be packaged as safety case evidence.

It is written for the library robot assurance case (`assurance/library_robot_case.yaml`, in this repository). It supports goal G6 "Building conditions do not invalidate the evidence" and evidence item EV-12 of that case. Where localisation is involved it also supports goal G4 and evidence item EV-08, as named in the case file.

Every item below is labelled **proposal** (specific enough to run once criteria are fixed) or **idea** (worth exploring, not yet specific).

## 2. How evidence is treated

This study follows `data/verification/PLAN.md`: rules are written before runs, access levels are recorded, and disagreement is reported, not hidden. Three consequences here.

1. **Documents versus interpretation.** Statements about what a source says cite table row IDs (for example D35) and the access level recorded there. Our own reading starts with "Interpretation:".
2. **Pre registration.** Acceptance criteria are written as criteria with named parameters. The values are fixed in a dated, hashed file committed before the first run of each test. Changing a value after results arrive is recorded as a deviation.
3. **Labelling results later.** Each future result carries a label for what produced it: `simulated`, `replayed`, `bench` or `field`. The Dhill evidence levels L0 to L3 may be reused for model based items (see section 8). A `simulated` result never supports a claim about hardware.

## 3. Common structure of the safety case argument

Each condition uses the same shape, attached under G6.

- **Claim:** the evidence already gathered for the robot (for example navigation, obstacle stopping, speed limits) remains valid when the named building condition occurs.
- **Argument, three steps:** (a) the condition is bounded and characterised for the site; (b) the robot is exercised across that bound, with its safety function measured; (c) outside the bound the robot detects the condition and moves to a safe state.
- **Evidence items:** the numbered items per condition.
- **Assumptions to state:** listed per condition. A claim without its assumptions is not made.

## 4. Heat

### 4.1 Evidence a developer could produce

- **H1 (proposal).** Site thermal envelope. Build a table of expected air temperature and solar load for each robot zone (entrance, atrium with glazing, service corridor, loading area, plant room adjacent area), from open weather data and a one day logger run with the robot's own temperature sensors.
- **H2 (proposal).** Component limit register. For each safety relevant component (battery, motor drivers, compute, LiDAR, cameras, brake or stop circuit), record the maker's stated temperature limit and its source page. Limits not found are listed as unknown, not assumed.
- **H3 (proposal).** Model prediction before test. Predict component temperatures for a defined mission and heat case, and file the prediction before the test.
- **H4 (proposal).** Safety function under heat. With the robot warm to the soak temperature in H1, measure stopping distance, protective stop response time and localisation error against the values recorded at reference conditions.
- **H5 (proposal).** Thermal limit response. Show the robot derates or parks before a component limit, and logs why.
- **H6 (idea).** Cold start after heat soak (a parked robot restarted in a hot vehicle or unconditioned store).

### 4.2 Safety case argument (under G6, EV-12)

- **Claim:** reference condition stopping and localisation evidence holds up to the site thermal envelope.
- **Step 1:** H1 and H2 show the envelope and the component limits, and the margin between them.
- **Step 2:** H3 and H4 show the safety functions meet the pre registered criteria inside the envelope, and the prediction matched measurement within the stated tolerance.
- **Step 3:** H5 shows behaviour near and beyond the limit.
- **Supporting items:** H1 to H5. H6 only if run.
- **Assumptions to state:** robot is indoor and the building cooling works; excursions outside the envelope (for example a cooling failure) are covered only by H5; the logged day represents the hottest relevant day (otherwise say how it differs).
- **Documents say:** IEC 60068-2-2 specifies dry heat tests for equipment used, transported or stored at high temperature, but the severities were not visible in the preview (D63, summary seen). IEC 60529 leaves solar radiation to the product standard (D62, full text seen, scope section). SORA OSO 24, "adverse environmental conditions", is Medium at SAIL III and High at SAIL IV to VI (D35, full text seen); the UK CAA text, as seen in a summary, says that at Medium the design shall perform in the stated environment with evidence, and that simulation must be justified for the target environment (D38, summary seen).
- Interpretation: the drone rules (D35, D38) and the dry heat method (D63) are the closest hooks. A library robot is not a drone, so they are borrowed method, not applicable requirements.

### 4.3 Free in simulation versus hardware

- **Free in simulation (proposal):** weather inputs from Open-Meteo or ERA5; thermal envelope decisions with Dhill (see section 8); mission replay in Gazebo or Webots under ROS 2 to produce the heat profile of a real route.
- **Needs hardware:** H1 (logger day), H4, H5, H6. Whether Gazebo and Webots model component heating in the way needed here was not checked (idea: confirm in their documentation). A heat chamber is not assumed; if none can be borrowed, H4 is run on the hottest natural day and labelled `field`.

### 4.4 Acceptance criteria (proposal, to fix before any run)

- AC-H1: predicted versus measured component temperature differs by no more than a tolerance T_h, set before the run.
- AC-H2: stopping distance and response time at soak are within a stated factor of the reference values, factor set before the run.
- AC-H3: derate or park starts at least a margin M_h below every limit in H2.
- A failed criterion is reported as a failure and stays in the case.

**What no source currently requires:** testing a ground robot against Gulf heat. Nearest: D63, D35, D38, D62; Dubai local climatic tests for autonomous vehicles appear only in press and summary form (D50, C65, both summary seen, secondary).

## 5. Dust

### 5.1 Evidence a developer could produce

- **DU1 (proposal).** Site dust characterisation: frequency of high PM10 days and entrance exposure, from open air quality data, and a log of visible dust on the robot after a defined period.
- **DU2 (proposal).** Ingress and fouling inspection plan: which openings, filters, heat sinks and sensor windows are exposed, with inspection before and after exposure.
- **DU3 (proposal).** Sensor degradation sweep. Degrade LiDAR and camera data in software (range loss, dropped returns, added noise, lens haze) across a stated range, and measure obstacle detection and stopping against the reference.
- **DU4 (proposal).** Dirty window check on hardware: apply a defined, documented contamination to the sensor window and repeat the obstacle test.
- **DU5 (proposal).** Detection of degradation: show the robot reports reduced sensing and slows or stops when the sweep exceeds the bound where DU3 fails.
- **DU6 (idea).** Cleaning interval derived from DU1 and DU3.
- **DU7 (idea).** A dust chamber test along the IEC 60529 route, if a laboratory is available at no cost to the study.

### 5.2 Safety case argument (under G6, EV-12)

- **Claim:** obstacle detection and stopping evidence holds under the dust exposure expected at the site, or the robot detects when it does not.
- **Step 1:** DU1 and DU2 bound the exposure.
- **Step 2:** DU3 and DU4 show the safety functions meet the criteria inside that bound.
- **Step 3:** DU5 shows the robot detects degradation beyond it and reaches a safe state.
- **Supporting items:** DU1 to DU5.
- **Assumptions to state:** the software degradation model resembles real fouling (this is checked only by DU4); cleaning is performed as scheduled; the window contamination in DU4 is representative.
- **Documents say:** PAS 1883 includes airborne dust and sand under particulates in its ODD environmental attributes, and excludes test procedures (D11, full text seen). IEC 60529 lists IEC 60068-2-68 (dust and sand) as a normative reference (D62, summary seen). IEC 61496-3 preview says outdoor application is not addressed (D65, summary seen).
- Interpretation: D11 gives a way to name dust as an ODD attribute but not to test it. That dust is outside the tested envelope of IEC 61496-3 is our reading, not text seen (as the table records for D65).

### 5.3 Free in simulation versus hardware

- **Free in simulation (proposal):** sensor noise and dropout in Gazebo or Webots; or degrade recorded ROS 2 bag files in software (DU3); PM10 history from Open-Meteo or ERA5 or another open air quality source (DU1).
- **Needs hardware:** DU2, DU4, DU7.

### 5.4 Acceptance criteria (proposal, to fix before any run)

- AC-DU1: at every degradation level up to the bound B_d, the obstacle is detected at a distance not less than the stopping distance plus margin.
- AC-DU2: beyond B_d, the robot enters a safe state within time t_d.
- AC-DU3: simulated and hardware results agree in direction at the DU4 contamination level; if not, DU3 is not used as evidence.

**What no source currently requires:** testing a robot's detection and stopping under Gulf dust. Nearest: D11, D62, D65, D35.

## 6. Glare

### 6.1 Evidence a developer could produce

- **GL1 (proposal).** Glare map. From building geometry, window orientation and computed sun position, list where and when direct sun can fall on the robot's camera or LiDAR along its routes.
- **GL2 (proposal).** Sensor behaviour log. Run each glare risk route at the times from GL1 and log image saturation, depth dropout and detection results.
- **GL3 (proposal).** Simulated sun sweep: vary sun elevation, azimuth and window reflection in simulation and measure detection performance.
- **GL4 (idea).** Glass and polished floor reflection cases (reflective surfaces for LiDAR).
- **GL5 (proposal).** Response: show the robot slows or stops when sensing is degraded by glare.

Glare items use the prefix GL, dust items the prefix DU, so that they are not confused with case goals G4 and G6 or with evidence table rows such as D11.

### 6.2 Safety case argument (under G6, EV-12)

- **Claim:** perception evidence from controlled indoor lighting holds under the sun conditions at the site, or the robot detects when it does not.
- **Step 1:** GL1 bounds where and when glare occurs.
- **Step 2:** GL2 and GL3 show detection and stopping meet the criteria across the bound.
- **Step 3:** GL5 shows the safe response.
- **Supporting items:** GL1, GL2, GL3, GL5.
- **Assumptions to state:** building geometry in the model is accurate; blinds or film are in their normal state (state it); sun conditions logged represent the worst season, or the gap is named.
- **Documents say:** PAS 1883 includes illumination and sun elevation and position as attributes; glare appears only as a detrimental effect in the text (D12, full text seen). IEC 61496-3 lists light interference tests and does not address outdoor application (D65, summary seen).
- Interpretation: D12 lets a developer name sun position as an ODD attribute; D65 suggests the closest test family is light interference tests for protective sensors. Neither requires glare testing in the Gulf.

### 6.3 Free in simulation versus hardware

- **Free in simulation (proposal):** GL3 in Gazebo or Webots using their lighting and sun settings (idea: confirm available settings in their documentation); building geometry from OpenStreetMap or the building plans (GL1); sun position computed in software.
- **Needs hardware:** GL2, GL4 (reflective surfaces), final GL5.

### 6.4 Acceptance criteria (proposal, to fix before any run)

- AC-GL1: detection rate of the standard obstacle set is at least p_g at every logged sun condition, p_g set before the run.
- AC-GL2: when saturation or depth dropout exceeds threshold s_g, speed is reduced within t_g.
- AC-GL3: any route and time where AC-GL1 fails is marked as a restriction in the case.

**What no source currently requires:** glare or low sun testing for a ground robot. Nearest: D12, D65.

## 7. GNSS degradation

**Safety boundary.** This protocol does not propose generating or transmitting GNSS jamming or spoofing RF signals. Items are limited to measurement level fault injection, replay of recorded public data, and simulation inside software. RF level tests need an authorised, shielded range and are out of scope.

For a library robot GNSS is probably not the main localisation source indoors. It matters for outdoor approaches, entrance transitions, time stamping and any shared fleet or campus function. The assumption is stated below.

### 7.1 Evidence a developer could produce

- **N1 (proposal).** GNSS dependency register: every function that uses GNSS position, velocity or time, and what it does when GNSS is lost or wrong.
- **N2 (proposal).** Fault injection at the measurement level in simulation: loss, noise growth, a position jump, a slow position drift and a replayed track, applied to the position stream in software only.
- **N3 (proposal).** Safe state check: for each injected fault, record detection time, localisation error, and whether the robot reaches the declared safe state.
- **N4 (proposal).** Replay of recorded public logs (for example open PX4 flight logs) through the same check, labelled `replayed`.
- **N5 (proposal).** Procedure evidence: a written procedure for loss or deterioration of GNSS, with a table exercise.
- **N6 (idea).** Cross check of GNSS time against an independent clock.

### 7.2 Safety case argument (under G4, EV-08 and G6, EV-12)

- **Claim:** localisation evidence (G4, EV-08) holds when GNSS is degraded, or the robot detects the degradation and moves to a safe state.
- **Step 1:** N1 shows where GNSS is used.
- **Step 2:** N2 to N4 show that each injected fault is detected within the pre registered time and the safe state is reached.
- **Step 3:** N5 shows procedures exist for faults the tests do not cover.
- **Supporting items:** N1 to N5.
- **Assumptions to state:** the fault models match real interference (this cannot be shown without RF level evidence, which is out of scope, so the claim is limited to the modelled faults); a second source of motion exists for drift detection; indoor operation does not depend on GNSS.
- **Documents say:** EASA SIB 2022-02 R4 recommends assessing the risk of losing GNSS, planning procedures without GNSS and monitoring GNSS against other sources, for commercial aircraft operators (D52, summary seen). The EASA AMC and GM row for drones (C34) is now title only: the final check could not confirm GNSS specific text, so it is not relied on. UAE working papers to ICAO report interference and suspected spoofing and ask for reporting frameworks (D57, D58, D59, all summary seen). Cabinet Resolution 110/2023 is reported to list a GPS feature among 17 test items for drone certification (C49, summary seen); Annex A is reported as binding for certification (C50, summary seen).
- Interpretation: D52 gives the structure (assess, detect, procedure) for aircraft; whether the drone guidance in C34 says the same is not confirmed. D57 to D59 show the issue is recognised nationally but none sets a robot test. The GPS feature test in C49 is for drones; its method was not seen.

### 7.3 Free in simulation versus hardware

- **Free in simulation (proposal):** N2, N3 and N4 using PX4 SITL with Gazebo, ROS 2, and log reading tools; positioning trust scoring from Marsad (section 8).
- **Needs hardware:** to apply any of this to the library robot, its real localisation stack must be logged (a `bench` result). Replay of that log can then be free.
- **Out of scope:** any RF generation or transmission.

### 7.4 Acceptance criteria (proposal, to fix before any run)

- AC-N1: each injected fault of size at least E_n is detected within time t_n in at least a fraction q_n of seeded runs.
- AC-N2: in every detected case the safe state is reached before position error exceeds the limit L_n set in the case.
- AC-N3: faults below E_n are listed as not covered. Missed detections are reported with seeds.

**What no source currently requires:** testing a ground robot against GNSS jamming or spoofing. Nearest: D52, D57, D58, D59, C48, C49, C50 (C34 not confirmed).

## 8. Reuse from the author's repositories

Linked, not copied. Statements follow each README only.

- **Dhill** (https://github.com/hudasol/dhill). Reuse: the GO, DERATE and PARK decision idea and the evidence levels L0 to L3 (README); the field test kit (`docs/field-test-kit.md`) and validation protocol (`docs/validation-protocol.md`) for how to instrument a robot; the pre registered prediction template (`docs/prediction-template.md`). The README states profiles are illustrative at L0, nothing is validated against field data, and no compliance claims are made. The README also states that no licence is selected yet, so reuse beyond linking needs the author's decision.
- **Marsad** (https://github.com/hudasol/marsad). Reuse: the vehicle trust states TRUSTED, DEGRADED and DENIED, the simulated scenarios, and PX4 log replay. The README states all results come from measurement level simulation, nothing has been run on real flight hardware or real interference data, and there is no RF signal generation. Licence stated there: Apache-2.0.

**What this protocol adds:** the assurance and evidence packaging layer. That is, how a result becomes safety case evidence: claim, argument, assumptions, pre registered criteria, labels for how a result was produced, and a statement of what no source requires. It does not add models. It does not claim that either repository satisfies any standard.

## 9. Deliberately excluded

- Any GNSS RF generation, transmission or SDR work.
- Any purchase, subscription, paid API or paid standard. Paid standards are cited at the level the table records.
- Compliance claims against any standard or authority; the cited instruments are hooks for method only.
- Thermal and sensor physics models (see Dhill, section 8).
- Outdoor robots, drones and vehicles as the system under test, except as borrowed method.
- Fire, flood and humidity cases, and cold.
- Attribution of any interference to any actor.

## 10. Free tools: licence status

`data/free_tools_licences.csv` lists only tools whose licence was read from a local package file or an official page: so far the tools this repository itself uses (PyYAML, pytest, detect-secrets, Graphviz). **None of the simulation or data tools below is confirmed.** Every attempt to fetch an official licence page was refused by the access controls of the retrieval setup on 2026-10-12, and we did not work around them. We name them as proposed free tools only. Each URL below is the page to check by hand.

**Unconfirmed**

| Tool | Use here | Page to check |
|---|---|---|
| Gazebo | simulation, sun and sensor noise | https://github.com/gazebosim/gz-sim/blob/main/LICENSE |
| Webots | simulation alternative | https://github.com/cyberbotics/webots/blob/master/LICENSE |
| ROS 2 | robot software, bag files | https://github.com/ros2/ros2/blob/rolling/LICENSE |
| PX4 SITL | GNSS fault simulation | https://github.com/PX4/PX4-Autopilot/blob/main/LICENSE |
| pyulog | read PX4 logs | https://github.com/PX4/pyulog/blob/master/LICENSE.md |
| Open-Meteo | weather and PM10 | https://open-meteo.com/en/license |
| ERA5 via Copernicus CDS | weather history (free account likely needed; check) | https://cds.climate.copernicus.eu/how-to-api |
| OpenStreetMap | building geometry | https://www.openstreetmap.org/copyright |
| GPSJam | context map of interference, not raw data (check terms) | https://gpsjam.org/about |

If any of these cannot be confirmed as free for this use, the dependent item is downgraded to an **idea**.

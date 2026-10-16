# ADR-0005 Small numpy models instead of a robot simulator

**Context.** The protocol names Gazebo, Webots, ROS 2 and PX4 as possible free tools, but their licences were not confirmed in the research phase, they are heavy to install, and bit for bit determinism across machines is hard to guarantee with them.

**Decision.** Write small, seeded numpy models for DU3, GL3 and N2 to N4 in `sim/`, label every output SYNTHETIC, and state that model and method share an author.

**Consequences.** Results reproduce byte for byte from one command and run in under a minute. The models are crude; LIMITATIONS says so, and PILOT describes how real logs would replace them.

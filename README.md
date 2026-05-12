# Mekdela Amba University Student Cafe Simulation

A 2D OpenGL simulation of the daily operations inside a student cafeteria at Mekdela Amba University. The project visualizes students obtaining tickets, queuing for food, dining at tables, and leaving, while demonstrating process queuing and resource allocation concepts using Python and OpenGL.

## 🚀 Overview

- Simulates a student cafeteria workflow in 2D using OpenGL.
- Visualizes ticketing, queue management, dining, and cleanup.
- Demonstrates core concepts such as **Process Queuing** and **Resource Allocation**.
- Built with Python and OpenGL libraries.

## 📝 Detailed Description

- Character animation logic includes walking motion for students, animated wing movement for menu selection, and hand reach animations during eating to convey realistic behavior.
- The simulation workflow begins at the ticket booth, proceeds through the food service queue, continues with dining at assigned tables, and ends with students moving toward the exit door.
- Table management uses discrete states: **Clean**, **Occupied**, and **Dirty**. Each table transitions based on student occupancy and cleanup actions to model resource allocation and turnover.
- Environmental details include proximity-based automated doors that respond as students approach, along with architectural elements such as walls, service counters, and dining areas that reinforce the cafeteria layout.
- The rendering system uses `glOrtho` to define the 2D coordinate system, while `glutTimerFunc` drives the update loop for smooth animation at approximately 60 FPS.
- These features are designed to illustrate **Process Simulation** concepts through visual queue handling, resource state transitions, and timed animation.

## 🧪 Tech Stack & Dependencies

- Language: `Python 3.x`
- Libraries:
  - `PyOpenGL`
  - `PyOpenGL_accelerate`
  - `FreeGLUT`
  - `math`
  - `random`

### Installation

```bash
pip install PyOpenGL PyOpenGL_accelerate
```

## 📁 Project Structure

- `alex.py` - Main logic, physics, rendering, and simulation flow.
- `MANIFEST` - Project metadata and repository manifest information.
- `version.txt` - Version tracking for the project.
- `.rsrc` - Resource files used by the simulation.

> Note: `__pycache__` and `.vscode` are excluded via `.gitignore`.

## ✨ Features

- **Ticket System(meal card)** at the booth for student entry and service.
- **Queue Management** for organized food service flow.
- **Table Management** with clean/dirty states and resource allocation.
- **Animated doors** and character walking logic to bring the scene to life.

## 🎮 Controls

- `R` - Reset the simulation
- `Q` or `ESC` - Quit the simulation

## ▶️ How to Run

```bash
python alex.py
```

Enjoy exploring the Mekdela Amba University Student Cafe Simulation and observing how queuing and resource management are represented visually in Python OpenGL.
# -MAU-student-cafe-simulation

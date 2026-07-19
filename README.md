# FPGA-Accelerated Conway's Game of Life (Hardware-in-the-Loop)

An interactive, hardware-in-the-loop implementation of Conway's Game of Life. This project pairs a high-performance Verilog core running on a Xilinx FPGA with a responsive Python/Pygame user interface. 

To bypass physical FPGA I/O limits, the project features a custom synthesis wrapper that compresses a $32 \times 32$ matrix stream down to a 5-pin physical interface.

![Conway's Game of Life Demo](demo.gif)

## 📖 The Story & Inspiration

This project was inspired by the classic **"Conway's Game of Life" challenge on HDLBits** (Problem: *Conwaylife*). 

While the original HDLBits problem focuses entirely on writing the 2D cell-update logic for a fixed $16 \times 16$ grid in a closed simulation environment, it leaves open a massive real-world engineering question: *How do you actually take this parallel hardware engine, scale it up, interact with it in real-time, and fit it onto a physical FPGA chip?*

When scaling the grid to $32 \times 32$ ($1,024$ cells), the core module required **2,051 parallel I/O pins** for simultaneous data loading and reading—instantly crashing the compiler because it exceeded physical hardware limits. This project bridges that exact gap between textbook HDL exercises and real hardware co-design by introducing:
1. A file-based semaphore architecture to allow an interactive Python GUI to talk directly to the hardware simulation loop.
2. A serial shift-register synthesis wrapper to compress the massive 2D matrix stream down to just 5 physical pins, allowing it to synthesize perfectly on a standard FPGA package.

*Note: Since my primary expertise lies in hardware description languages rather than desktop GUI frameworks, the Python/Pygame interface code was co-developed with the assistance of AI to quickly build a robust, clean visual frontend.*

## 🚀 Features
*   **Hardware-Accelerated Core:** Fully parallel, synthesis-optimized neighbor-evaluation logic with toroidal (wrap-around) boundaries inspired by HDLBits.
*   **Dual-Mode Architecture:** 
    *   *Simulation Mode:* Wide parallel I/O for high-throughput, file-based simulation testing.
    *   *Synthesis Mode:* Serial shift-register interface to comply with physical FPGA package limitations.
*   **Interactive Python GUI:** Built with Pygame featuring standard control sets, grid state injection, and a "Deep Sea Cobalt" theme.

## 📊 Hardware Resource Utilization

Synthesized using Xilinx Vivado targeting an **AMD/Xilinx Artix-7 FPGA (Part: xc7a35tcpg236-1)**. 

### Resource Metrics ($32 \times 32$ Grid)
| Resource | Used | Available | Utilization % |
| :--- | :--- | :--- | :--- |
| **Slice LUTs** | 5,013 | 20,800 | 24.1% |
| **Slice Registers** | 2,049 | 41,600 | 4.9% |
| **Bonded IOB** | 5 | 106 | 4.7% |
| **BUFGCTRL** | 1 | 32 | 3.1% |

*Note: The core engine consumes 1,024 of the registers to preserve the active state of the cell grid, while the remaining registers manage the wrapper's internal shift logic.*

## 📁 Repository Structure
```text
├── game_of_life.v             # Verilog Core & Synthesis Shift-Register Wrapper
├── game_of_life_tb_verify.v   # Hardware-in-the-loop Simulation Testbench
├── ui_controller.py          # Python/Pygame Graphical User Interface
├── demo.gif                   # Animation showcase of the Pygame interface
└── README.md                  # Project Documentation

## 🛠️ Getting Started

### Prerequisites
*   Xilinx Vivado
*   Python 3.x
*   Pygame (`pip install pygame`)

### Running the Hardware-in-the-Loop Simulation

Because the hardware simulation engine and the Python frontend run as separate processes, you must start the Vivado simulation first so it can process the interactive UI events.

#### Step 1: Start the Vivado Hardware Engine
1. Open your project in Xilinx Vivado.
2. In the **Sources** panel, expand **Simulation Sources**, right-click `game_of_life_pipeline_tb`, and select **Set as Top**.
3. In the left-hand Flow Navigator panel, click **Run Simulation** -> **Run Behavioral Simulation**.
4. Once the waveform window opens, look at the bottom of the Vivado window for the **Tcl Console** tab.
5. In the console command line, type `run -all` and press **Enter**. *Note: This tells the simulator to run indefinitely, allowing it to actively poll the communication files for inputs from the UI.*

#### Step 2: Start the Pygame Interface
1. Open a terminal or command prompt in your project folder.
2. Run the Python interface script:
   ```bash
   python ui_controller.py

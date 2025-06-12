# TradeMind Setup Guide for Windows

## Introduction

This guide is designed for Quantitative Traders who are new to the TradeMind algorithmic trading platform and wish to set up the system in a local Windows environment. While a background in quantitative finance, statistics, and Python programming is strongly recommended for leveraging the full capabilities of TradeMind, this document focuses specifically on the initial installation, build process, and basic launch procedures.

By following the steps outlined below, you will:

*   Clone the TradeMind repository from GitHub.
*   Build the core C++ components.
*   Install the Python package for strategy development.

Deep knowledge of C++ or complex distributed systems infrastructure is not required to complete these initial setup tasks. This guide will provide you with a foundational understanding of how to get TradeMind operational on your system. Subsequent guides will cover understanding configuration files and running the platform.

## I. Prerequisites: Setting Up Your Windows Development Environment

Before cloning and building TradeMind, you need to install several development tools and libraries.

### 1. Install Visual Studio Build Tools (or Visual Studio IDE)

TradeMind's C++ components on Windows are best built with the MSVC compiler.

1.  Go to the [Visual Studio Downloads page](https://visualstudio.microsoft.com/downloads/).
2.  **Option A (Recommended if you don't need the full IDE, e.g., if you prefer using VSCode):**
    *   Download "Build Tools for Visual Studio 2022" (or your preferred recent version).
    *   Run the installer.
    *   In the "Workloads" tab, select "Desktop development with C++".
    *   In the "Installation details" pane on the right, ensure the following (or their equivalents for your VS version) are checked:
        *   MSVC v143 VS 2022 C++ x64/x86 build tools (or latest compatible version for C++17)
        *   Windows SDK (e.g., Windows 11 SDK or a recent Windows 10 SDK)
        *   C++ CMake tools for Windows
    *   Click "Install".
3.  **Option B (If you want the full IDE):**
    *   Download "Visual Studio Community 2022" (or another version).
    *   Run the installer and select the "Desktop development with C++" workload. This will typically include all necessary components mentioned above.
4.  After installation, **restart your system**.

### 2. Install CMake

CMake is used to generate the build files for TradeMind.

1.  Go to the [CMake download page](https://cmake.org/download/).
2.  Download the "Windows x64 Installer" for the latest stable release.
3.  Run the installer. During installation, make sure to select either **"Add CMake to the system PATH for all users"** or **"Add CMake to the system PATH for the current user"**.

### 3. Install Git

Git is required to clone the TradeMind source code repository.

1.  Go to the [Git for Windows download page](https://git-scm.com/download/win).
2.  Download and run the installer. The default options are usually fine.

### 4. Install vcpkg (C++ Package Manager)

vcpkg simplifies acquiring and building C++ library dependencies for MSVC.

1.  Choose an installation directory for vcpkg. For example, `C:\dev\vcpkg`. We'll refer to this as `<vcpkg_root>`.
2.  Open a Command Prompt or PowerShell terminal and clone vcpkg:
    ```bash
    cd C:\dev
    git clone https://github.com/microsoft/vcpkg.git
    cd vcpkg
    ```
3.  Bootstrap vcpkg:
    ```bash
    .\bootstrap-vcpkg.bat
    ```
4.  Integrate vcpkg with your development environment (user-wide):
    ```bash
    .\vcpkg integrate install
    ```
    This step allows CMake to automatically find libraries installed by this vcpkg instance. You should see a message confirming user-wide integration.

### 5. Install Core C++ Dependencies via vcpkg

Using the same terminal window, still inside your `<vcpkg_root>` directory (e.g., `C:\dev\vcpkg`), install the following libraries for the x64-windows triplet:

```bash
.\vcpkg install boost:x64-windows
.\vcpkg install zeromq:x64-windows
.\vcpkg install yaml-cpp:x64-windows
.\vcpkg install poco[core,foundation,xml,net,netssl,util,json]:x64-windows --recurse
.\vcpkg install tbb:x64-windows
```

### 6. Prepare Your VS Code Environment (Optional, if using VSCode)

1.  If you don't have it, install [Visual Studio Code](https://code.visualstudio.com/).
2.  Install the following extensions from the VS Code Marketplace:
    *   C/C++ Extension Pack (by Microsoft)
    *   CMake Tools (by Microsoft)
3.  After installing these extensions, restart VS Code.
4.  When you open the TradeMind project later, you'll need to select a CMake Kit:
    *   Open the Command Palette (Ctrl+Shift+P or View > Command Palette).
    *   Type "CMake: Select a Kit" and choose it.
    *   Select an MSVC kit that matches your Visual Studio Build Tools installation and desired architecture (e.g., "Visual Studio Build Tools 2022 Release - amd64"). This tells CMake Tools to use the MSVC compiler.

You have now set up the core prerequisites. The next step is to get the Fix8 library, which requires manual building on Windows for a CMake-based project.

## II. Building and Preparing the Fix8 Library

The TradeMind project requires the Fix8 library for FIX protocol support. We will build it from source using its Visual Studio solution and then prepare it for use with TradeMind's CMake build.

1.  **Clone the Fix8 Source Code:**
    *   Choose a directory to store the Fix8 source code (separate from your TradeMind project). For example, `C:\dev_libs\fix8_source`.
    *   Open a Command Prompt or Git Bash:
        ```bash
        md C:\dev_libs
        cd C:\dev_libs
        git clone https://github.com/FIX8Group/fix8.git fix8_source
        ```

2.  **Build Fix8 using MSBuild:**
    *   Open an **"x64 Native Tools Command Prompt for VS 2022"** (or the equivalent for your VS version). This prompt has the necessary environment variables set for MSBuild.
    *   Navigate to the Fix8 MSVC solution directory (e.g., `fix8_source\msvc` or a similar path within the cloned Fix8 repo):
        ```bash
        cd C:\dev_libs\fix8_source\msvc
        ```
        *(Note: The exact path to the `.sln` file might vary depending on the Fix8 library version; locate the appropriate Visual Studio solution file, e.g., `fix8-vc143.sln` or `fix8-vc142.sln`)*.
    *   Restore NuGet packages (replace `fix8-vc143.sln` with the actual solution file name):
        ```bash
        nuget restore fix8-vc143.sln
        ```
        (If `nuget.exe` isn't in your path or recognized, you might need to add it to PATH or use the MSBuild equivalent: `msbuild fix8-vc143.sln /t:Restore`)
    *   Build the solution (ensure the solution filename matches):
        ```bash
        msbuild fix8-vc143.sln /p:Configuration=Release /p:Platform=x64 /t:Build
        ```

3.  **Create a Custom "Install" Directory for Fix8:**
    To make it easy for TradeMind's CMake build to find the necessary Fix8 files, copy them to a structured location.
    *   Create the following directory: `C:\local_libs\fix8_install`
    *   Inside `C:\local_libs\fix8_install`, create these subdirectories: `include`, `lib`, `bin`.
    *   **Copy Header Files:**
        *   Source: `C:\dev_libs\fix8_source\include\fix8\`
        *   Destination: `C:\local_libs\fix8_install\include\fix8\`
        *   (Ensure all `.h` and `.hpp` files, including `f8config.h`, are copied into this `fix8` subdirectory).
    *   **Copy Library Files:**
        *   Source: `C:\dev_libs\fix8_source\msvc\x64\Release\bin\*.lib` (or the specific output path for `.lib` files from your Fix8 build if different)
        *   Destination: `C:\local_libs\fix8_install\lib\`
        *   (Copy all generated `.lib` files from the source to the destination directory).
    *   **Copy Executable and DLL Files:**
        *   Source `f8c.exe`: `C:\dev_libs\fix8_source\msvc\x64\Release\bin\f8c.exe`
        *   Destination `f8c.exe`: `C:\local_libs\fix8_install\bin\f8c.exe`
        *   Source `fix8.dll`: `C:\dev_libs\fix8_source\msvc\x64\Release\bin\fix8.dll`
        *   Destination `fix8.dll`: `C:\local_libs\fix8_install\bin\fix8.dll`
    *   **Copy Dependency Files (e.g., `getopt.dll`):**
        *   `f8c.exe` might require `getopt.dll`. This DLL would have been a dependency during the Fix8 MSVC build. Locate `getopt.dll` (it might be in `C:\dev_libs\fix8_source\msvc\x64\Release\bin\` or a NuGet package cache).
        *   Source: Location of `getopt.dll`
        *   Destination: `C:\local_libs\fix8_install\bin\getopt.dll`
        *   *Note: Test by running `f8c.exe --version` from `C:\local_libs\fix8_install\bin\`. If it reports missing DLLs, locate them (likely from the Fix8 build output or system paths if common redistributables) and copy them to this `bin` directory.*

You now have a self-contained installation of the MSVC-built Fix8 library.

## III. Cloning and Building the TradeMind C++ Components

With all prerequisites and the Fix8 library prepared, you can now clone and build TradeMind.

1.  **Clone the TradeMind Repository:**
    *   Choose a directory for your TradeMind project (e.g., `C:\Users\YourUserName\Documents\GitHub\`).
    *   Open a terminal window:
        ```bash
        cd C:\Users\YourUserName\Documents\GitHub\
        git clone https://github.com/Sun-GOD/trademind.git
        cd trademind
        ```

2.  **Prepare TradeMind's CMake Configuration:**
    *   Locate the `FindFix8.cmake` file. This file is typically provided by the Fix8 library developers for CMake integration. You might find it within the Fix8 source tree you cloned (e.g., in a `contribs/cmake/`, `cmake/`, or similar subdirectory of `C:\dev_libs\fix8_source`).
    *   Create a directory named `cmake_modules` inside your `trademind` project root (e.g., `C:\Users\YourUserName\Documents\GitHub\trademind\cmake_modules`).
    *   Copy the `FindFix8.cmake` file into this `trademind/cmake_modules/` directory.

3.  **Configure TradeMind using CMake:**

    *   **Using VS Code (Recommended if set up):**
        *   Open your `trademind` project folder in VS Code.
        *   Ensure your MSVC Kit is selected (as per step I.6).
        *   VS Code's CMake Tools extension should prompt to configure. If not, trigger it: Press Ctrl+Shift+P, type "CMake: Configure", and select it.
        *   Review the CMake output in the "Output" panel (select "CMake" from the dropdown). It should find all dependencies (Boost, ZeroMQ, YAML-CPP, Poco, TBB, Fix8). You should see messages like "Configuring done" and "Generating done". Build files are typically placed in a `build` subdirectory within `trademind`.

    *   **Using Command Line (Alternative):**
        *   Open a Developer Command Prompt for VS (e.g., "x64 Native Tools Command Prompt for VS 2022").
        *   Navigate to your `trademind` project directory.
        *   Create a build directory and navigate into it:
            ```bash
            mkdir build
            cd build
            ```
        *   Run CMake. You'll need to tell CMake where to find vcpkg's toolchain file and your custom Fix8 installation. The `FindFix8.cmake` module might require `Fix8_ROOT` to be set, or it might search common paths.
            ```bash
            cmake .. -DCMAKE_TOOLCHAIN_FILE=C:/dev/vcpkg/scripts/buildsystems/vcpkg.cmake -DFix8_ROOT=C:/local_libs/fix8_install
            ```
            (Adjust paths if your `<vcpkg_root>` or `C:\local_libs\fix8_install` locations are different. The `FindFix8.cmake` script might also need other hints if `Fix8_ROOT` is not sufficient.)

4.  **Build TradeMind:**

    *   **Using VS Code:**
        *   Click the "Build" button in the status bar (often looks like a cog or simply says "[Build]").
        *   Alternatively, press Ctrl+Shift+P, type "CMake: Build", and select it. Choose the desired configuration (e.g., Debug or Release).

    *   **Using Command Line (if configured via command line):**
        *   Ensure you are in the `trademind\build` directory.
        *   Run:
            ```bash
            cmake --build . --config Release
            ```
            (Or `--config Debug` for a debug build).

    This will compile the project. The executable (`trademind.exe`) will be placed in a subdirectory of your build folder (e.g., `trademind/build/bin/Release/`). Successful builds usually end with a message indicating completion with exit code 0.

You have now successfully built the C++ components for TradeMind.

## IV. Setting Up the Python Environment for Strategy Development

TradeMind uses Python for developing and backtesting trading strategies via its `pyquant` library.

1.  **Python Installation:**
    *   **Recommended Python Version**: Due to dependencies like TensorFlow (which `pyquant` might rely on indirectly or directly for advanced features), it's recommended to use a Python version between **3.9 and 3.10.5 (inclusive)**.
    *   **Installation**: Download Python from [python.org](https://www.python.org/). During installation on Windows, ensure you check the box that says **"Add Python X.X to PATH"**.

2.  **Create a Python Virtual Environment (Highly Recommended):**
    This isolates project-specific dependencies and avoids conflicts.
    *   Open your preferred command-line interface.
    *   Navigate to your TradeMind project's root directory:
        ```bash
        cd C:\Users\YourUserName\Documents\GitHub\trademind
        ```
    *   Create the virtual environment (e.g., named `.venv`):
        ```bash
        python -m venv .venv
        ```
    *   Activate the virtual environment:
        ```bash
        .venv\Scripts\activate
        ```
    Your command prompt should now be prefixed with `(.venv)`.

3.  **Install the TradeMind Python Package (`pyquant`):**
    *   Ensure your virtual environment `(.venv)` is active.
    *   Navigate to the `python` subdirectory within your TradeMind project:
        ```bash
        cd python
        ```
    *   Install the `pyquant` package in editable mode (`-e`). This means changes you make to the source code in the `python` directory are immediately reflected:
        ```bash
        pip install -e .
        ```

Your Python environment is now prepared for TradeMind strategy development.

## V. Next Steps

With the development environment set up and core components built, you can proceed to:

*   Understanding TradeMind configuration files (refer to the *TradeMind Configuration Guide*).
*   Running the TradeMind platform.
*   Developing your first trading strategy (refer to the *Developing Your First Trading Strategy with TradeMind* tutorial and the *TradeMind Python API Reference*).
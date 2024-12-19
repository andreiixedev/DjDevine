<div align="center">
<img src="docs/Logo.png" width="50%">
 <br><h1>DJDevine</h1><br>
 A discord radio bot for your soul :D
</div>
<br>

# What 'DJDevine' is
It's a discord bot that plays radio stations by adding what radio you want, it gives you the freedom to add any radio you want, offering multiple server support

<details>

<summary><b>What's uses DJDevine</b></summary>
- FFMPEG (to play radio stations)<br>
- Discord.py 
- Psutil (to retrieve information from the system for the debug command)
</details>

# How do I run it?
<b>LINUX</b>
1. **Install Python, pip and FFMPEG:**

    ```bash
    sudo apt update
    ```
    ```bash
    sudo apt install ffmpeg python3 python3-pip python3-venv -y
    ```
    ```bash
    python3 -m venv venv
    ```
    ```bash
    source venv/bin/activate
    ```
    ```bash
    cd /path/to/your/bot
    ```
    ```bash
    pip install -r requirements.txt
    ```
    ```bash
   python3 main.py
   ```

<b>WINDOWS</b>
1. **Install Python and pip**:
   - Download and install Python from [python.org](https://www.python.org/downloads/).
   - Make sure to check the box **"Add Python to PATH"** during installation.
   - Verify the installation:
     ```bash
     python --version
     pip --version
     ```

2. **Install FFMPEG**:
   - Download the latest FFmpeg build from [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
   - Extract the archive to a folder (e.g., `C:\ffmpeg`).
   - Add `C:\ffmpeg\bin` to your **System Environment Variables**.

3. **Install dependencies**:
   - Navigate to the bot folder:
     ```bash
     cd C:\your\bot\path
     ```
   - Install Python dependencies:
     ```bash
     pip install -r requirements.txt
     ```

4. **Run the script**:
   ```bash
   python main.py
   ```
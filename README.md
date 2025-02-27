# hackrf-broadcast-to-text

Capture radio broadcasts using HackRF, decode signals, and convert speech to text.

## **Instructions to Set Up and Use a HackRF**

This guide includes setup instructions for **WSL2** and **Linux/Ubuntu**.

---

## **HackRF Setup in WSL2**

### **1. Install Dependencies**

Run the following in **PowerShell (Admin)**:

```powershell
wsl --update
winget install usbipd
```

Then restart your system.

### **2. Enable USB Passthrough**

1. List available USB devices:
   ```powershell
   usbipd.exe list
   ```
2. Bind HackRF:
   ```powershell
   usbipd bind --busid 2-3
   ```
3. Attach HackRF to WSL2 (**replace **``** with actual BusID**):
   ```powershell
   usbipd.exe attach --wsl --busid 2-3
   ```

### **3. Verify HackRF in WSL**

Open **WSL** and check if it's recognized:

```bash
hackrf_info
```

### **4. Test HackRF**

To record RF data:

```bash
hackrf_transfer -r test.raw -f 155355000 -s 2000000 -g 40 -l 40 -n 2000000
```

Check the Output File:

```bash
ls -lh test.raw
```

To start a TCP listener:

```bash
nc -lvp 12345
```

---

## **HackRF Setup on Linux/Ubuntu**

### **1. Install Dependencies**

```bash
sudo apt update
sudo apt install -y hackrf gnuradio gr-osmosdr libhackrf-dev
```

### **2. Verify HackRF Installation**

Check if HackRF is detected:

```bash
hackrf_info
```

### **3. Test HackRF**

Record RF data:

```bash
hackrf_transfer -r test.raw -f 155355000 -s 2000000 -g 40 -l 40 -n 2000000
```

Check the Output File:

```bash
ls -lh test.raw
```

### **4. Set Up Real-Time Audio Processing**

#### **Install Dependencies**

```bash
sudo apt install -y portaudio19-dev python3-pyaudio
```

#### **Install Vosk for Speech-to-Text**

```bash
sudo apt install -y python3-pip python3-dev
pip3 install vosk --break-system-packages
```

#### **Run Real-Time Processing**

Demodulate FM in real-time:

```bash
python3 demod_fm_realtime.py -f 155355000 --rf-gain 16 --if-gain 22 -t 12345
```

Real-time transcription:

```bash
python3 realtime_transcribe.py
```

---

## **Troubleshooting**

**Error: Resource Busy**

```bash
sudo fuser -v /dev/hackrf*
sudo kill -9 <PID>
```

**Error: Address Already in Use**

```bash
sudo netstat -tulnp | grep 12345
sudo kill -9 <PID>
```



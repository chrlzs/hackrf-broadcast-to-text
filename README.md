# hackrf-broadcast-to-text
Capture radio broadcasts using HackRF, decode signals, and convert speech to text

# **instructions to set up and use a HackRF in WSL2**

## **HackRF Setup in WSL2**  

## **1. Install Dependencies**  
Run the following in **PowerShell (Admin)**:  
```powershell
wsl --update
winget install usbipd
```
Then restart your system.  

## **2. Enable USB Passthrough**  
1. List available USB devices:  
   ```powershell
   usbipd.exe list
   ```

```powershell
PS C:\Users\cbron> usbipd list
Connected:
BUSID  VID:PID    DEVICE                                                        STATE
1-11   1462:7c56  USB Input Device                                              Not shared
1-14   0b05:190e  ASUS USB-BT500                                                Not shared
2-1    05ac:024f  USB Input Device                                              Not shared
2-3    1d50:6089  HackRF One                                                    Shared
6-4    1050:0402  USB Input Device                                              Not shared
7-2    1532:0085  USB Input Device, Razer Basilisk V2                           Not shared
7-3    30be:0100  I'm Fulla Schiit, USB Input Device                            Not shared
7-4    3537:1010  Xbox Gaming Device                                            Not shared

Persisted:
GUID                                  DEVICE
```
2. Bind HackRF
   ```powershell
   usbipd bind --busid 2-3
   ```
3. Attach HackRF to WSL2 (**replace `2-3` with actual BusID**):  
   ```powershell
   usbipd.exe attach --wsl --busid 2-3
   ```

   ```powershell
   usbipd: info: Using WSL distribution 'Ubuntu' to attach; the device will be available in all WSL 2 distributions.
   usbipd: info: Detected networking mode 'nat'.
   usbipd: info: Using IP address 172.23.144.1 to reach the host.
   ```

## **3. Verify HackRF in WSL**  
Open **WSL** and check if it's recognized:  
```bash
hackrf_info
```

```bash
hackrf_info version: 2023.01.1
libhackrf version: 2023.01.1 (0.8)
Found HackRF
Index: 0
Serial number: 0000000000000000644064XXXXXXXXXX
Board ID Number: 2 (HackRF One)
Firmware Version: local-608c8c35 (API:1.04)
Part ID Number: 0xa000cb3c 0x00784f64
```

## **4. Test HackRF**  

Capture a Signal:

To record RF data:  
```bash
hackrf_transfer -r test.raw -f 155355000 -s 2000000 -g 40 -l 40 -n 2000000
```

-r test.raw: Save the raw IQ data to test.raw.

-f 155355000: Tune to 155.355 MHz.

-s 2000000: Set the sample rate to 2 MS/s.

-g 40 and -l 40: Set the gain levels. //Issue: Low Volume - Adjust the gain settings 

-n 2000000: Capture 2 million samples. //Issue: High Latency -  Reduce the buffer size in the TCP/UDP sink block.

Check the Output File:

```bash
ls -lh test.raw
```

To start a TCP listener:
```bash
nc -lvp 12345
```

# **Real-Time Audio Processing Pipeline**

charlie@ZENTRAL:/mnt/d/source/hackrf-broadcast-to-text$ sudo apt install pipx

charlie@ZENTRAL:/mnt/d/source/hackrf-broadcast-to-text$ pipx ensurepath

charlie@ZENTRAL:/mnt/d/source/hackrf-broadcast-to-text$ pipx install vosk

# **Receiving Audio Data in Python**

1.) Install PortAudio (Required for pyaudio):
```bash
sudo apt update
sudo apt install portaudio19-dev python3-pyaudio
```
2.) Verify Installation:
```bash
sudo apt install portaudio19-dev python3-pyaudio
```

## **Install Vosk**
```bash
sudo apt update 

sudo apt install python3-pip python3-dev

sudo pip3 install vosk --break-system-packages #TODO: Handle this more gracefully

python3 -m pip show vosk

```

Demodulate FM real-time:

```bash
$ python3 demod_fm_realtime.py -f 155355000 --rf-gain 16 --if-gain 22 -t 12345
```

Real-time transscription
```bash
$ python3 realtime_transcribe.py
```

# **Troubleshooting**

RuntimeError: Failed to open HackRF device (-1000) Resource busy

sudo fuser -v /dev/hackrf*

```bash
                     USER        PID ACCESS COMMAND
/dev/bus/usb/001/002:
                     charlie    8973 F.... python3
```

```bash

sudo kill -9 8973

```

---

```bash

OSError: [Errno 98] Address already in use

```

sudo netstat -tulnp | grep 12345

sudo kill -9 1158

```

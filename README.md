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
Serial number: 0000000000000000644064dc086699cd
Board ID Number: 2 (HackRF One)
Firmware Version: local-608c8c35 (API:1.04)
Part ID Number: 0xa000cb3c 0x00784f64
```

## **4. Test HackRF**  
To record RF data:  
```bash
hackrf_transfer -r test.raw -s 10e6
```

## **5. Install GNURadio (Optional for GUI Workflows)**  
```bash
sudo apt install gnuradio
gnuradio-companion
```

## **Troubleshooting**  
- If HackRF isn’t detected, ensure USB passthrough is enabled:  
  ```powershell
  usbipd.exe attach --wsl --busid <BusID>
  ```
- If permission errors occur:  
  ```bash
  sudo chmod 666 /dev/hackrf*
  ```


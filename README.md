# hackrf-broadcast-to-text
Capture radio broadcasts using HackRF, decode signals, and convert speech to text

# radio-text-capture

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
   usbipd bind --busid 7-1
   ```
3. Attach HackRF to WSL2 (**replace `7-1` with actual BusID**):  
   ```powershell
   usbipd.exe attach --wsl --busid 7-1
   ```

## **3. Verify HackRF in WSL**  
Open **WSL** and check if it's recognized:  
```bash
hackrf_info
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


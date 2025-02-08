# hackrf-broadcast-to-text
Capture radio broadcasts using HackRF, decode signals, and convert speech to text

# radio-text-capture

# **instructions to set up and use a HackRF in WSL2.  **

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
3. Bind HackRF
   ```powershell
   usbipd bind --busid 7-1
   ```
2. Attach HackRF to WSL2 (**replace `7-1` with actual BusID**):  
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


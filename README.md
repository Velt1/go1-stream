# go1-stream

## **Overview**
`go1-stream` offers a way to combine multiple camera streams into a single output, structured in a customizable 4x4 grid. Define each grid section's camera source for flexibility and ease of use.
You can get creative and built a socket connection in that changes the way the grid positions the individual streams without interrupting the output stream.

## **Benefits**

- **Bandwidth Efficiency**: Streamline your data usage with just one unified stream.
- **Jetson Nano Compatibility**: Address the incompatibility of Jetson Nanos with CUDA.

## **Installation and Usage**

### **1. Set up the MediaMtx Server**
Begin by installing the MediaMtx Server on your Go1 RaspberryPI. The necessary resources are available at the [MediaMtx Repository](https://github.com/bluenviron/mediamtx).

### **2. Forwarding the Webcam Streams**

#### **Sender Configuration**:

**Nano 13**:
```bash
ffmpeg -f v4l2 -framerate 15 -video_size 680x480 -i /dev/video1 -an -c copy -f mpjpeg 'udp://192.168.123.161:5001'
ffmpeg -f v4l2 -framerate 15 -video_size 680x480 -i /dev/video0 -an -c copy -f mpjpeg 'udp://192.168.123.161:5002'
```

**Nano 14**:
```bash
ffmpeg -f v4l2 -framerate 15 -video_size 680x480 -i /dev/video1 -an -c copy -f mpjpeg 'udp://192.168.123.161:5003'
ffmpeg -f v4l2 -framerate 15 -video_size 680x480 -i /dev/video0 -an -c copy -f mpjpeg 'udp://192.168.123.161:5004'
```

#### **Proxy Configuration**:

**RaspberryPI**:
```bash
sudo nice -n -20 ffmpeg -i udp://192.168.123.161:5001 -c copy -f mpjpeg udp://192.168.123.15:5011 
sudo nice -n -20 ffmpeg -i udp://192.168.123.161:5002 -c copy -f mpjpeg udp://192.168.123.15:5012 
sudo nice -n -20 ffmpeg -i udp://192.168.123.161:5003 -c copy -f mpjpeg udp://192.168.123.15:5013 
sudo nice -n -20 ffmpeg -i udp://192.168.123.161:5004 -c copy -f mpjpeg udp://192.168.123.15:5014 
```
### **3. Running the Multiplexer**
Transfer the multiplexer.py script to your NX 15 and run it.

**Final Output**:
After completing the above steps, access the unified streams at:
```bash
http://ROBOT_IP:8889/stream/
```
### Caution
The script is resource-intensive and performs optimally when no other CPU-heavy scripts are running. I suggest terminating the 'unitree' processes before starting.
If it exeeds 100% CPU, try sudo nvpmodel -m 0 on the NX.

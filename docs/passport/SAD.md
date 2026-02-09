# Software Architecture Document for Project Proper Physical Education

## 0. Authors
| Name           | Github       | Role                    |
| -------------- | ------------ | ----------------------- |
| Ruslana Babich | @Rasymptote  | Application development |
|                |              |                         |
| Artem Kutsenko | @Artemius951 | Sensor development      |
|                |              |                         |
| Matvey Solovev | @fresh-ops   | Application development |

## 1. Goals and limitations
### 1.1. Key functional requirements
- The system shall analyze therapeutic exercise execution in real time.
- The system shall support two independent data sources:
    1. computer vision 
    2. electromyography
- The system shall support individual EMG calibration.
- User data shall be compared with reference exercises.
- The system shall generate context-aware recommendations during exercise execution.
- The system shall generate training and progress reports.

### 1.2. Non-functional requirements
1. Performance
    - System must process data and provide user feedback with latency not exceeding 150 ms.
    - EMG sensors and cameras data update rate must be at least 30 Hz.
2. Accuracy
    - Skeleton keypoint recognition accuracy using MediaPipe must be at least 95% under good lighting conditions.
    - Exercise type identification accuracy must be at least 90% for exercises in reference database.
3. Hardware
    - **RAM**: 8 GB or more
    - **Ports**: Minimum 4 USB 3.0 ports
4.  Software
    - **OS**: Windows 10/11 64-bit or Ubuntu 20.04 LTS and above
5. Physical Environment
    - Well-lit room
    - Minimum distance from cameras to user - 2 meters
    - No background interference (foreign movements in frame)
    - User must wear fitted clothing that doesn't conceal body contours

### 1.3. Architectural goals
- The system must support synchronized processing of video and EMG streams.
- The system must be modular and extensible, allowing new exercises and analysis rules to be added without major architectural changes.
- The system must be tolerant to noisy and incomplete data, especially from EMG sensors.
- The system must produce human-readable recommendations.
### 1.4. Additional goals, restrictions and preferences
- The architecture should allow future integration of additional sensors.


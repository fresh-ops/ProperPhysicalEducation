# Software Requirements Specification for Project Proper Physical Education
## Authors
- Ruslana Babich
- Maksim Zaugolnikov
- Artem Kutsenko
- Matvey Solovev
## Introduction
The system is designed to monitor the correct execution of therapeutic physical exercises using two technologies: electromyography (EMG) and computer vision.
The EMG component of the system consists of four wireless sensors (two for each arm) that record muscle electrical activity. The computer vision component creates a digital skeleton of a user. 
The obtained data is compared with recommendations described in medical literature and used to generate user recommendations, which will help to make the exercises correctly. Using the system user can monitor the progress of trainings via reports. 
## Glossary
- **EMG (Electromyography)** - method for recording muscle electrical activity
- **EMG Sensor** - device for recording and transmitting muscle activity data
- **Muscle Activity** - level of electrical activity in the recorded muscle(measuered in volts)
- **Baseline Level** - level of muscle activity in a relaxed state
- **Peak Activity** - maximum level of muscle activity during exercise
- **Expert System** - computer system capable of partially replacing a human expert in resolving problematic situations
- **Data Vectorization** - process of converting raw data into numerical vectors
- **Vector Database** - specialized data management system designed for efficient storage, indexing, and search of vector embeddings
- **Knowledge Base** - collection of **facts** and **rules** that describe the subject domain
- **PT (Physical Therapy)** - set of exercises aimed at prevention and rehabilitation after injuries
- **Reference Exercise** - exemplary exercise execution used for comparison with user data
- **Digital Skeleton** - a simplified representation of a patient body
## Actors
### Patient
#### Role
User performing therapeutic physical exercises
#### Goals
- Receive feedback on exercise correctness
- Monitor rehabilitation progress
- Avoid mistakes during exercise execution
## Functional Requirements
### Use Cases: EMG Measurement Subsystem
#### UC-EMG-001: EMG Sensor Calibration
**Actors**: Patient
**Goals**:
- Improve measurement accuracy
**Precondition**: Sensors are attached to user's arms; System software is running normally  
**Trigger condition**: Calibration procedure initiation  
**Main success scenario**:
1. System prompts user to relax arm muscles
2. Records baseline activity level for each muscle (30 seconds)
3. Prompts user to perform reference muscle tension
4. Records maximum activity level
5. Saves calibration coefficients for each sensor

**Alternative scenario: UnreasonableMeasure**
**Trigger condition**: The measures system recieves are out of reasanoble bounds
1. System detects unstable or unexpected measurement patterns
2. System notifies user about the need to repeat calibration
3. System restarts calibration procedure

**Alternative scenario: SensorsConnectionFailed**  
**Trigger condition**: System cannot connect to sensors
1. System stops execution and notifies user about connection error
### Use Cases: Expert System Subsystem

#### UC-ES-001: Execution Recommendations
**Actors**: Patient
**Goals**:
- Provide real-time exercise recommendations
- Receive clear and timely feedback for immediate movement correction
**Preconditions**: Exercise data has been obtained and identified
**Trigger condition**: Exercise type is determined
**Main success scenario**:
1. Expert System compares received exercise data with reference data in knowledge base (reference angles and muscle activity levels/ranges)
2. Discrepancies with reference execution are identified 
3. Specific recommendations are generated 
4. Recommendations are displayed to user
#### UC-ES-002: Training Report
**Actors**: Patient
**Goals**:
- Generate training session report
- Track rehabilitation progress dynamics
**Preconditions**: System has been operating in normal mode during training
**Trigger condition**: Training session completion
**Main success scenario**:
1. System collects all measurement data from training session
2. Data is compared with previous readings (number of repetitions, movement amplitude, muscle activity stability, number of recommendations given)
3. Rehabilitation progress report is generated
4. Report is provided to user (in form of graphs, tables, text summary with PDF export capability)
## Non-Functional Requirements
### 1. Performance
- System must process data and provide user feedback with latency not exceeding 150 ms
- EMG sensors and cameras data update rate must be at least 30 Hz
### 2. Accuracy
- Skeleton keypoint recognition accuracy using MediaPipe must be at least 95% under good lighting conditions
- Exercise type identification accuracy must be at least 90% for exercises in reference database
### 5. Technical Environment Requirements

#### 5.1. Hardware
- **RAM**: 8 GB or more
- **Ports**: Minimum 4 USB 3.0 ports
#### 5.2. Software
- **OS**: Windows 10/11 64-bit or Ubuntu 20.04 LTS and above
#### 5.3. Physical Environment
- Well-lit room
- Minimum distance from cameras to user - 2 meters
- No background interference (foreign movements in frame)
- User must wear fitted clothing that doesn't conceal body contours

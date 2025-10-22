# Software Requirements Specification for Project Proper Physical Education
## Authors
- Ruslana Babich
- Maksim Zaugolnikov
- Artem Kutsenko
- Matvey Solovev
## Introduction
The system is designed to monitor the correct execution of therapeutic physical exercises using two technologies: electromyography (EMG) and computer vision. The EMG component of the system consists of four wireless sensors (two for each arm) that record muscle electrical activity. The obtained data is compared with recommendations described in medical literature and used to generate user recommendations.
## Glossary
- **EMG (Electromyography)** - method for recording muscle electrical activity
- **EMG Sensor** - device for recording and transmitting muscle activity data
- **EMG Sleeve** - specialized mount for securing sensors on limbs
- **Muscle Activity** - level of electrical activity in the recorded muscle
- **Baseline Level** - level of muscle activity in a relaxed state
- **Peak Activity** - maximum level of muscle activity during exercise
- **Expert System** - computer system capable of partially replacing a human expert in resolving problematic situations
- **Neural Network** - mathematical model, as well as its software or hardware implementation, built on the principle of nervous network organization
- **Data Vectorization** - process of converting raw data into numerical vectors
- **Vector Database** - specialized data management system designed for efficient storage, indexing, and search of vector embeddings
- **MediaPipe** - cross-platform open-source framework from Google designed for building machine learning pipelines operating in real-time
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
### System Components
#### EMG Measurement Subsystem
- Collects data from EMG sensors
- Filters measurement noise
#### Computer Vision Subsystem
- Collects camera input
- Creates digital skeleton model
- Determines angles between limbs
#### Expert System Subsystem
- Prepares collected data
- Identifies exercises
- Determines exercise correctness
- Provides recommendations
## Functional Requirements
### Use Cases: EMG Measurement Subsystem
#### UC-EMG-001: EMG Sensor Calibration
**Actors**: Patient, System  
**Goals**:
- Patient: improve measurement accuracy
- System: establish baseline muscle activity levels  
**Precondition**: Sensors are attached to user's arms; System software is running normally  
**Trigger condition**: Calibration procedure initiation  
**Main success scenario**:
1. System prompts user to relax arm muscles
2. Records baseline activity level for each muscle (30 seconds)
3. Prompts user to perform reference muscle tension
4. Records maximum activity level
5. Saves calibration coefficients for each sensor

**Alternative scenario: UserFailsCalibration**  
**Trigger condition**: User refuses to perform required actions or performs them incorrectly
1. System detects unstable or unexpected measurement patterns
2. System notifies user about the need to repeat calibration
3. System restarts calibration procedure

#### UC-EMG-002: EMG Data Recording
**Actors**: System  
**Goals**:
- Collect and transmit patient muscle activity data  
**Preconditions**: Sensors are properly attached and calibrated; System software is running normally  
**Trigger condition**: Exercise execution begins  
**Main success scenario**:
1. EMG Subsystem receives data from sensors
2. Received data is filtered to eliminate noise
3. Processed data is sent to Expert System

**Alternative scenario: SensorsConnectionFailed**  
**Trigger condition**: EMG Subsystem cannot connect to sensors
1. System stops exercise execution and notifies user about connection error
### Use Cases: Computer Vision Subsystem
#### UC-CV-001: Angular Data Acquisition
**Actors**: System
**Goals**:
- Build digital skeleton and determine angles between limbs
- Provide patient posture data
**Preconditions**: Cameras are installed and calibrated; System software is running normally
**Trigger condition**: Exercise execution begins
**Main success scenario**:
1. Computer Vision Subsystem connects to cameras
2. Skeleton projections are built from camera images
3. Projections are converted into digital skeleton
4. Angles between limbs are calculated
5. Data is transmitted to Expert System

**Alternative scenario: CamerasConnectionFailed**  
**Trigger condition**: Computer Vision Subsystem cannot connect to cameras
1. System terminates exercise execution and displays error message to Patient

**Alternative scenario: UserNotFound**  
**Trigger condition**: Computer Vision Subsystem cannot detect Patient in camera images
1. System warns Patient about skeleton detection error and retries
2. After 3 unsuccessful attempts, system pauses execution and notifies user
### Use Cases: Expert System Subsystem
#### UC-ES-001: Exercise Identification
**Actors**: System
**Goals**:
- Identify current exercise being performed by Patient
**Preconditions**: System is operating in normal mode during exercise
**Trigger condition**: Expert System receives data from EMG and Computer Vision Subsystems
**Main success scenario**:
1. Received data (angles from CV and muscle activity from EMG) is converted into unified feature vector
2. Feature vector is processed by calculating probability for each known exercise
3. If maximum probability exceeds threshold X, exercise is considered identified
4. Exercise type is saved in current session context

**Alternative scenario: NoSuchExercise**  
**Trigger condition**: System cannot identify exercise type (all probabilities below threshold X)
1. System notifies user about recognition error and offers list of predefined exercises
#### UC-ES-002: Execution Recommendations
**Actors**: Patient, System
**Goals**:
- Provide real-time exercise recommendations
- Receive clear and timely feedback for immediate movement correction
**Preconditions**: Exercise data has been obtained and identified
**Trigger condition**: Exercise type is determined
**Main success scenario**:
1. Expert System compares received exercise data with reference data in knowledge base (reference angles and muscle activity levels/ranges)
2. Discrepancies with reference execution are identified (e.g., "Excessive muscle potential in antagonist muscle", "Insufficient elbow flexion angle")
3. Specific recommendations are generated (e.g., "Relax biceps", "Raise arm 10 degrees higher")
4. Recommendations are displayed to user
#### UC-ES-003: Training Report
**Actors**: Patient, System
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
- **CPU**: Minimum 4 cores, equivalent to Intel Core i5 10th generation or better
- **GPU**: Recommended discrete graphics card for stable computer vision operation
- **RAM**: 8 GB or more
- **Ports**: Minimum 4 USB 3.0 ports
#### 5.2. Software
- **OS**: Windows 10/11 64-bit or Ubuntu 20.04 LTS and above
- **Python Interpreter**: Version 3.10
#### 5.3. Physical Environment
- Well-lit room
- Minimum distance from cameras to user - 2 meters
- No background interference (foreign movements in frame)
- User must wear fitted clothing that doesn't conceal body contours

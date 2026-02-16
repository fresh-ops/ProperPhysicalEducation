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
- The system must be tolerant to noisy and incomplete data
## 2. Goals analysis
This section analyzes the key architectural goals defined in Section 1.3.  
For each goal, possible solution approaches are considered, along with their applicability, advantages, and limitations in the context of the Proper Physical Education system.
### 2.1. Synchronized processing of video and EMG streams
The system must process computer vision data and EMG data in a synchronized manner in order to correctly evaluate exercise execution and generate meaningful recommendations.
#### Possible approaches
1. Sequential processing: video data and EMG data are processed one after another in a single execution flow.
2. Centralized data acquisition: all raw data is collected by a single controller module that distributes synchronized samples to subsystems.
3. Parallel processing with shared time reference: video and EMG subsystems operate independently, producing time-stamped data that is synchronized at the expert system level.
#### Analysis
- Sequential processing is not suitable, as delays in one data source would block the entire pipeline and violate real-time constraints.
- Centralized acquisition increases coupling and reduces modularity.
- Parallel processing with time-stamped synchronization is the most appropriate solution. In this approach:
	- Computer vision and EMG subsystems run independently.
	- Each data sample is tagged with a timestamp.
    - The expert system consumes synchronized data based on time proximity
#### Advantages
- Meets real-time requirements.
- Preserves subsystem independence.
- Scales well for future extensions.
#### Disadvantages
- Requires synchronization and buffering mechanisms. 
### 2.2. Modularity and extensibility of the system
The system must be modular and extensible, allowing new exercises and analysis rules to be added without major architectural changes.
#### Possible approaches
1. Hardcoded exercise logic: exercise rules are implemented directly in application code. 
2. Configuration-driven exercise descriptions: exercises and postures are described using external configuration files defining expected joint angles and constraints.
3. Data-driven pose descriptions combined with a rule-based expert system:
    - Reference poses are described using external JSON files.
    - An expert system applies analysis rules on top of these descriptions to identify exercises and evaluate correctness.
#### Analysis
- Hardcoded logic is not extensible and leads to frequent code changes.
- Pure configuration-driven descriptions allow defining reference poses but are insufficient for expressing complex reasoning and corrective logic.
- A data-driven approach combined with a rule-based expert system is the most suitable solution. In this approach:
	- JSON files store structured descriptions of reference poses, including joint angle ranges and posture constraints.
	- These descriptions act as a knowledge base of reference data.
	- A rule-based expert system operates on top of this data to identify the performed exercise, detect deviations from reference poses, generate human-readable corrective recommendations
#### Advantages
- Clear separation between reference data and decision logic.
- High extensibility: new exercises can be added by introducing new JSON descriptions.
#### Disadvantages
- Requires careful design and validation of pose description formats.
### 2.3. Tolerance to noisy and incomplete data
The system must remain stable and reliable when processing noisy or partially missing data.
#### Possible approaches
1. Data filtering: values received from devices pass through a filter, which reduces the risk of data contamination by outliers.
2. Machine learning: in conditions of incomplete data, it is possible to restore it using context through machine learning methods.
#### Analysis
- Data filtering is a standard method for working in noisy conditions, while it does not consume significant resources either for implementation or for execution on the machine.
- Machine learning provides potentially greater resilience to incomplete data; however, our team has no experience working with it, which would complicate development and contribute to schedule delays. This direction should be considered for further development rather than as a necessary approach.
#### Advantages
- Low overhead
- Standard practice, well described in literature
#### Disadvantages
- Lower effectiveness in complex conditions
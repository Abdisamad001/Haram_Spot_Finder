# HARAM AVAILABLE SPOT DETECTION 

This project is a Streamlit-based application that uses YOLOv8 object detection to identify available prayer spots from uploaded videos or images.

This is how the overall architecture and design of the system works, illustrating how user inputs, YOLOv8 detection, database operations, and output visualization are connected in a streamlined workflow.

![System Architecture](./asset/System%20Architecture.svg)



## Live Demo
The application is deployed and accessible at:
[Haram Available Spot Detection](https://haramspotfinder-f2ntqrqjzygjc6g9hzhov9.streamlit.app/)


### 🚀 Installation & Setup

#### 1. Environment Setup
##### Create conda environment
```bash
conda create -p venv python==3.9.0 -y
```

##### ⚡ Activate environment
```bash
conda activate ./venv
```

#### 2. Clone Repository:
`git clone https://github.com/Abdisamad001/Haram_Spot_Finder.git` 

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run Application 
```bash
streamlit run app.py
```
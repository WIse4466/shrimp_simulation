# clone the project
```bash!
git clone git@github.com:WIse4466/shrimp_simulation.git
```
```bash!
cd shrimp_simulation
```
# Set up environment

use venv to build virtual environment
```bash!
python -m venv venv
```

activate virtual environment

Windows
```bash!
venv\Scripts\activate
```
macOS/Linux
```bash!
source venv/bin/activate
```
Install required packages
```bash!
pip install -r requirements.txt
```
# Run simulation
```bash!
python3 simulation.py
```
or
```bash!
python simulation.py
```
# Launch server
```bash!
python -m http.server
```
# Open UI
Enter http://localhost:8000/ in your browser

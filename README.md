# clone the project
```bash!
git clone git@github.com:WIse4466/shrimp_simulation.git
```
```bash!
cd shrimp_simulation
```
# Set up environment
```bash!
# 在專案根目錄執行
# 使用 venv 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```
```bash!
pip install -r requirements.txt
```
# Run simulation
```bash!
# 在 backend 目錄下執行
python3 simulation.py
or 
python simulation.py
```
# Launch server
```bash!
python -m http.server
```
# Open UI
Enter http://localhost:8000/ in your browser



pip install gurobipy

from gurobipy import Model, GRB, quicksum

# 調整價格範圍：350 ± 150 = 200-500，更精細的區間
price_options = [200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400, 420, 440, 460, 480, 500]

# 重新調整需求函數參數，讓高價格時顧客數合理下降
b = [83, 78, 73, 68, 63, 58, 53, 48, 38, 23, 15, 13, 11, 9, 7, 5]
a = [20, 19, 17, 15, 13, 11, 9, 7, 5, 3, 1, -1, -3, -5, -7, -9]
cost_per_shrimp = 15
labor_cost_fixed = 667
rod_limit = 20
y_min, y_max = 5, 15
M = 1000

n = len(price_options)
model = Model("ShrimpFishing_Piecewise")

# 決策變數
z = model.addVars(n, vtype=GRB.BINARY, name="z")
y = model.addVar(lb=y_min, ub=y_max, vtype=GRB.INTEGER, name="y")
q = model.addVars(n, lb=0, ub=y_max, vtype=GRB.CONTINUOUS, name="q")
customers = model.addVar(name="total_customers")

# 約束條件
model.addConstr(quicksum(z[i] for i in range(n)) == 1, name="ChooseOnePrice")

for i in range(n):
    model.addConstr(q[i] <= M * z[i], name=f"BigM1_{i}")
    model.addConstr(q[i] <= y, name=f"BigM2_{i}")
    model.addConstr(q[i] >= y - M * (1 - z[i]), name=f"BigM3_{i}")

model.addConstr(customers == quicksum(a[i] * q[i] + b[i] * z[i] for i in range(n)),
                name="TotalCustomers")
model.addConstr(customers / 11 <= rod_limit, name="RodLimit")

# 目標函數
revenue = 2 * quicksum(price_options[i] * (a[i] * q[i] + b[i] * z[i]) for i in range(n))
shrimp_cost = 2 * cost_per_shrimp * customers * y
profit = revenue - shrimp_cost - labor_cost_fixed

model.setObjective(profit, GRB.MAXIMIZE)
model.Params.NonConvex = 2
model.optimize()

if model.status == GRB.OPTIMAL:
    chosen_idx = [i for i in range(n) if z[i].X > 0.5][0]
    chosen_price = price_options[chosen_idx]
    chosen_customers = customers.X

    print(f"\n✅ 最優價格: {chosen_price}")
    print(f"🧍 顧客總數: {chosen_customers:.0f}")
    print(f"🦐 人均蝦量(y): {y.X:.2f} 公斤/小時/人")
    print(f"💰 最大利潤: {model.ObjVal:.2f}")

    print("\n[詳細資訊]")
    print(f"收入: {revenue.getValue():.2f}")
    print(f"蝦成本: {shrimp_cost.getValue():.2f}")
    print(f"固定人工成本: {labor_cost_fixed}")
    print(f"需求函數: {a[chosen_idx]}*{y.X:.2f} + {b[chosen_idx]} = {chosen_customers:.0f}")

    # 顯示所有價格選項的詳細分析
    print("\n[各價格選項分析]")
    for i in range(n):
        if z[i].X > 0.5:
            customers_at_price = a[i] * y.X + b[i]
            revenue_at_price = 2 * price_options[i] * customers_at_price
            cost_at_price = 2 * cost_per_shrimp * customers_at_price * y.X + labor_cost_fixed
            profit_at_price = revenue_at_price - cost_at_price
            print(f"★ 價格 {price_options[i]}: 顧客{customers_at_price:.0f}人, 收入{revenue_at_price:.0f}, 利潤{profit_at_price:.0f}")
        else:
            customers_at_price = a[i] * y.X + b[i]
            revenue_at_price = 2 * price_options[i] * customers_at_price
            cost_at_price = 2 * cost_per_shrimp * customers_at_price * y.X + labor_cost_fixed
            profit_at_price = revenue_at_price - cost_at_price
            print(f"  價格 {price_options[i]}: 顧客{customers_at_price:.0f}人, 收入{revenue_at_price:.0f}, 利潤{profit_at_price:.0f}")

else:
    print("❌ 未找到最優解")
    print(f"模型狀態: {model.status}")

print("\n[參數設定檢查]")
print(f"價格範圍: {min(price_options)}-{max(price_options)} (中心點約{(min(price_options)+max(price_options))/2})")
print(f"放蝦量範圍: {y_min}-{y_max} 公斤/小時/人")
print(f"釣竿限制: {rod_limit} 支")
print(f"蝦成本: {cost_per_shrimp} 元/公斤")
print(f"固定成本: {labor_cost_fixed} 元")
prices = "250,450,1700,35.40"
markup = 120

for price in prices.split(","):
    costprice = float(price) * (100/(100+markup))
    grossprofit = float(price) - costprice
    
    print("Cost Price:", costprice, "|", "Gross Profit:", grossprofit)
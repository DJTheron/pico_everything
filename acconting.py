prices = "330,176,1144,1738"
markup = 120

for price in prices.split(","):
    costprice = float(price) * (100/(100+markup))
    grossprofit = float(price) - costprice # add proper want/have calc
    
    print("Cost Price:", costprice, "|", "Gross Profit:", grossprofit)
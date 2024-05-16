import pandas as pd
import numpy as np

def calculate_bmi ():
    weights = df['Weight']
    heights = df['Height']
    bmi = []
    for w,h in zip(weights, heights):
        b = w/(h*h)
        bmi.append(b)
    return bmi

data = [
    {"Name": "Asabeneh", "Country":"Finland","City":"Helsinki"},
    {"Name": "David", "Country":"UK","City":"London"},
    {"Name": "John", "Country":"Sweden","City":"Stockholm"}]
df = pd.DataFrame(data)
print(df)
weights = [74, 78, 69]
df['Weight'] = weights
heights = [173, 175, 169]
df['Height'] = heights
print(df)
df['Height'] = df['Height'] * 0.01
bmi = calculate_bmi()
df['BMI'] = bmi
print(df)
df['BMI'] = round(df['BMI'], 2)
print(df)
birth_year = ['1769', '1985', '1990']
current_year = pd.Series(2020,index=[0,1,2])
df['Birth Year'] = birth_year
df['Current Year'] = current_year

df['Birth Year'] = df['Birth Year'].astype('int')
df['Current Year'] = df['Current Year'].astype('int')
ages = df['Current Year'] - df['Birth Year']
df['Ages'] = ages
# 将'Ages'列转换为浮点数类型
df['Ages'] = df['Ages'].astype(float)
print(df)
# df[df['Ages'] > 120]['Ages'] = df[df['Ages'] < 120]['Ages'].describe()['mean']
mean_age_under_120 = df[df['Ages'] < 120]['Ages'].mean()
# 将年龄大于120岁的记录设置为这个平均值
df.loc[df['Ages'] > 120, 'Ages'] = mean_age_under_120
print(df)
df.to_csv('people.csv', index=False)
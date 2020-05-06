import pandas as pd

# Create Pandas dataframe from the data
df = pd.DataFrame({'x': [10,20,30,450], 'y': [1,2,3,4]})
df.index += 1

# Create Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('pandas_simple.xlsx', engine='xlsxwriter')

# Write the data frame to the BytesIO object.
df.to_excel(writer, sheet_name="Sheet1")

writer.save()
import numpy as np

a = np.array([[2,0,3],
              [1,2,6],
              [1,3,2],])

row_locator = a[:,1]==2 # Rows where 2 is in the column 1

row_values = []

for x in range(0, len(a)):
    if row_locator[x]:
        row_values.append(x)

print(row_values)
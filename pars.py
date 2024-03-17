import pandas as pd
from itertools import cycle
import os
import time

current_dir_path = os.path.dirname(__file__)
data_file_path = os.path.join(current_dir_path, 'links_test.xlsx')

data = pd.read_excel(data_file_path)
print(data)
abc = pd.read_excel(data_file_path).shape
print(abc)

# links = [x for x in data['Ссылка']]
# print(links)

print(data['Ссылка'][0])
print(data['Ссылка'][1])
# for i in data['Наименование']:
#     print(i)
# names = data['Ссылка']
# # names = [x for x in data['Наименование']]
# print(names)


# for i in cycle(data['Ссылка']):
#     print(i)
#     time.sleep(0.1)

# for i in cycle([1, 2, 3]):
#     print(i)

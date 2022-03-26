import pandas as pd
import numpy as np
import csv
#! -------獲取座標-------
df = pd.read_csv('TSP/test10.csv')

node_ori = list(df.iloc[:, 0])
x_coord_ori = list(df.iloc[:, 1])
y_coord_ori = list(df.iloc[:, 2])

node = [str(x) for x in node_ori]
x_coord = [x for x in x_coord_ori]
y_coord = [x for x in y_coord_ori]

'''
XY = zip(x_coord, y_coord)
coords = dict(zip(node, XY))  # 將編號與座標存為字典
# print(coords)
'''

XY = zip(x_coord, y_coord)
coords = list(XY)  # 將編號與座標存為字典
print(coords)
#! -------計算距離矩陣-------
dist = []
for i in range(0, len(node_ori)):
    for j in range(0, len(node_ori)):
        a = ((x_coord_ori[i] - x_coord_ori[j])**2 +
             (y_coord_ori[i] - y_coord_ori[j]) ** 2) ** 1 / 2
        # print(a)
        dist.append(a)

dist = [dist[i:i+len(node_ori)]
        for i in range(0, len(dist), len(node_ori))]
# print(dist)

#! -------將距離矩陣存入excel-------
output = open('distance_matrix1.xls', 'w', encoding='utf-8')
for i in range(len(dist)):
    for j in range(len(dist[i])):
        output.write(str(dist[i][j]))  # 因為write無法寫入int資料，故先將資料型態轉為str
        output.write('\t')  # 相當於按了Tab一下，換下一格
    output.write('\n')  # 寫完一子list換行
output.close()

#! -------GA撰寫-------
max_evolution_num = 200  # 迭代次數
population_num = 100  # 族群數
cross_pro = 0.6  # 交配機率
mutation_pro = 0.1  # 變異機率
best_gens = [-1 for _ in range(len(coords))]  # 菁英染色體(基因排列)
min_distance = np.inf  # 最短路徑長度
best_fit_index = 0  # 最短路徑出現的代數
start = 0  # 種群的初始位置


#! -------TSP撰寫-------
gene_len = len(coords)
chroms = []
for i in range(population_num):
    gene = list(range(gene_len))
    np.random.shuffle(gene)  # ? random.shuffle 順序隨機打亂
    for j, g in enumerate(gene):    # ? 使起點為0
        if g == start:
            gene[0], gene[j] = gene[j], gene[0]
    chroms.append(gene)
    print(chroms[i])

for i in range(len(chroms)):
    gens = np.copy(chroms[i])
    gens = np.append(gens, gens[0]).tolist()
    chroms[i] = gens
    print(chroms[i])

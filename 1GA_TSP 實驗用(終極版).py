from os import remove
import RegExService
import numpy as np
import matplotlib.pyplot as plt
import random
import operator
import math

#! -------指定檔案-------
fileName = 'TSP/att48.txt'


# TODO 計算距離
def distance(vec1, vec2):
    return np.linalg.norm(np.array(vec1) - np.array(vec2))


#! 計算各點間距離
def compute_dis_mat(num_city, location):
    dis_mat = np.zeros((num_city, num_city))
    for i in range(num_city):
        for j in range(num_city):
            if i == j:
                dis_mat[i][j] = np.inf
                continue
            a = location[i+1]
            b = location[j+1]
            tmp = np.sqrt(
                sum([(parent1[0] - parent1[1]) ** 2 for parent1 in zip(a, b)]))
            dis_mat[i][j] = tmp
    return dis_mat


#! 貪婪初始解
def greedy_init(dis_mat, num_city):
    start_index = 0
    result = []
    for i in range(population_num):
        rest = [parent1 for parent1 in range(0, num_city)]
        if start_index >= num_city:
            start_index = np.random.randint(0, num_city)
            result.append(result[start_index].copy())
            continue
        current = start_index
        rest.remove(current)
        # ? 貪婪法
        result_one = [current]
        while len(rest) != 0:
            tmp_min = math.inf
            tmp_choose = -1
            for parent1 in rest:
                if dis_mat[current][parent1] < tmp_min:
                    tmp_min = dis_mat[current][parent1]
                    tmp_choose = parent1

            current = tmp_choose
            result_one.append(tmp_choose)
            rest.remove(tmp_choose)
        result.append(result_one)
        start_index += 1
    return result


# TODO 初始化種群(生成基因的隨機排列)
def init_chromos(start=-1, gene_len=-1):
    chroms = []  # 所有種群
    for i in range(population_num):
        gene = list(range(gene_len))
        np.random.shuffle(gene)  # ? random.shuffle 順序隨機打亂
        if start != -1:  # ? 使起點為0
            for j, g in enumerate(gene):
                if g == start:
                    gene[0], gene[j] = gene[j], gene[0]
            chroms.append(gene)
    return chroms


#! 計算路徑長度
def compute_pathlen(path, dis_mat):
    result = 0

    for i in range(len(path) - 1):
        a = path[i]
        b = path[i + 1]
        result += dis_mat[a][b]
    return result


#! 適合度評分
def compute_adp(fruits):
    adp = []
    for fruit in fruits:
        if isinstance(fruit, int):
            import pdb
            pdb.set_trace()
        length = compute_pathlen(fruit, dis_mat)
        adp.append(1.0 / length)
    return np.array(adp)


# TODO 適合度評分
def calc_fin_ness(citys, gens):
    gens = np.copy(gens)
    gens = np.append(gens, gens[0])  # ? 染色體末端加上起點(回到起點)
    D = compute_pathlen(gens, dis_mat)  # ? 路線距離加總
    return 1.0 / D


# TODO 累計機率輪盤法
def roulette_gambler(fit_pros, chroms):
    fit_pros_total = sum(fit_pros)  # ? 0.0006368504551314806
    pick = np.random.random()
    p = 0
    for j in range(len(chroms)):
        p += fit_pros[j] / fit_pros_total
        # print(p)
        if p >= pick:
            return j


#! 染色體選擇(透過適合度的分數與輪盤法，來選出菁英染色體)
def choice_parents(citys, chroms):
    n = len(chroms)
    fit_pros = []
    [fit_pros.append(calc_fin_ness(citys, chroms[i])) for i in range(n)]
    fit_pros = np.array(fit_pros)

    sort_index = np.argsort(-fit_pros).copy()
    sort_index = sort_index[0:int(choice_pro * len(sort_index))]

    parents = []
    parents_score = []
    for index in sort_index:
        parents.append(chroms[index])
        parents_score.append(fit_pros[index])

    return parents


#! 染色體選擇(透過適合度的分數與輪盤法，來選出菁英染色體)
def choice(citys, chroms):
    n = len(chroms)
    fit_pros = []
    [fit_pros.append(calc_fin_ness(citys, chroms[i])) for i in range(n)]
    # print(fit_pros)
    choice_gens = []
    for i in range(n):
        j = roulette_gambler(fit_pros, chroms)  # ? 利用輪盤法選出好的染色體
        choice_gens.append(chroms[j])  # ? 加入選擇的染色體族群當中
    for i in range(n):
        chroms[i] = choice_gens[i]  # ? 選擇後的染色體族群取代原本的染色體族群
    return chroms


#! 交配
def cross(chroms):
    gens_len = len(chroms[0])
    while len(chroms) < population_num:
        index1 = np.random.randint(1, gens_len - 1)  # ? 第一切點   -1
        index2 = np.random.randint(index1, gens_len + 1)  # ? 第二切點  +1
        if index1 == index2:
            continue
        n = len(chroms)
        fit_pros = []
        [fit_pros.append(calc_fin_ness(citys, chroms[i])) for i in range(n)]
        parent1 = roulette_gambler(fit_pros, chroms)  # ? 利用輪盤法選出好的染色體
        parent2 = roulette_gambler(fit_pros, chroms)

        if parent1 == parent2:
            continue

        temp_gen1 = chroms[parent1][index1:index2+1]  # 交配的基因片段1
        temp_gen2 = chroms[parent2][index1:index2+1]  # 交配的基因片段2

        # 交配、插入基因片段
        temp_parent1, temp_parent2 = np.copy(
            chroms[parent1]).tolist(), np.copy(chroms[parent2]).tolist()
        temp_parent1[index1:index2+1] = temp_gen2
        temp_parent2[index1:index2+1] = temp_gen1
        # 消除衝突
        pos = index1 + len(temp_gen1)  # 插入交配基因片段的结束位置
        conflict1_ids, conflict2_ids = [], []
        [conflict1_ids.append(i) for i, v in enumerate(temp_parent1) if v in temp_parent1[index1:pos]
         and i not in list(range(index1, pos))]  # ? i引數；v為值
        [conflict2_ids.append(i) for i, v in enumerate(temp_parent2) if v in temp_parent2[index1:pos]
         and i not in list(range(index1, pos))]
        for i, j in zip(conflict1_ids, conflict2_ids):
            temp_parent1[i], temp_parent2[j] = temp_parent2[j], temp_parent1[i]

        x_adp = calc_fin_ness(citys, temp_parent1)
        y_adp = calc_fin_ness(citys, temp_parent2)
        if x_adp > y_adp and (not temp_parent1 in chroms):
            chroms.append(temp_parent1)
        elif x_adp <= y_adp and (not temp_parent2 in chroms):
            chroms.append(temp_parent2)

    return chroms


# TODO 突變
def mutation(chroms):
    n = len(chroms)
    gens_len = len(chroms[0])
    for i in range(n):
        index1 = np.random.randint(1, gens_len - 2)
        index2 = np.random.randint(1, gens_len - 2)
        if index1 == index2:
            continue
        cur_pro = np.random.random()  # ? 決定是否要突變
        # 不突變
        if cur_pro > mutation_pro:
            continue
        chroms[i][index1], chroms[i][index2] = chroms[i][index2], chroms[i][index1]
    return chroms


# TODO 染色體反轉
def reverse(citys, chroms):
    n = len(chroms)
    gens_len = len(chroms[0])
    for i in range(n):
        flag = 0
        while flag == 0:
            index1 = np.random.randint(1, gens_len - 2)
            index2 = np.random.randint(index1, gens_len - 2)
            if index1 == index2:
                continue
            temp_chrom = np.copy(chroms[i])
            temp_chrom = temp_chrom.tolist()
            temp_gen = temp_chrom[index1:index2+1]
            temp_gen.reverse()
            temp_chrom[index1:index2 + 1] = temp_gen
            fit_score1 = calc_fin_ness(citys, chroms[i])
            fit_score2 = calc_fin_ness(citys, temp_chrom)
            # 如果反轉後的染色體比原本的還好
            if fit_score2 > fit_score1:
                chroms[i] = temp_chrom  # ? 更新染色體為反轉後的染色體
            flag = 1
    return chroms


def draw_H(citys, best_gens):
    plt.ion()
    x_data = [(v[0]) for i, v in enumerate(citys)]
    y_data = [(v[1]) for i, v in enumerate(citys)]
    parent1, parent2 = [], []
    plt.cla()
    plt.scatter(x_data, y_data, s=10, c='blue')
    for i, v in enumerate(best_gens):
        parent2.append(citys[v])
        plt.annotate(s=v, xy=citys[v], xytext=(-4, 5),
                     textcoords='offset points', fontsize=10)
    x_data = [(v[0]) for i, v in enumerate(parent2)]
    y_data = [(v[1]) for i, v in enumerate(parent2)]
    plt.title("Kuan-Ting Wu TSP", fontsize=25)
    plt.text(min(x_data) * 1.2, min(y_data) * 1.2, "Total distance=%.2f" %
             min_distance, fontdict={'size': 20, 'color': 'red'})
    plt.xlim(min(x_data) * 1.2, max(x_data)*1.2)
    plt.ylim(min(y_data) * 1.2, max(y_data)*1.2)
    plt.plot(x_data, y_data, 'r-')
    plt.pause(0.00000001)


if __name__ == '__main__':
    coords = RegExService.getData(fileName)
    citys = list(coords.values())

    max_evolution_num = 500  # ? 迭代次數
    population_num = len(citys)  # ? 族群大小
    choice_pro = 0.2  # !
    cross_pro = 0.8  # ? 交配機率
    mutation_pro = 0.2  # ? 突變機率
    best_gens = [-1 for _ in range(len(citys))]  # ? 精英染色體
    min_distance = np.inf  # ? 最短路徑長度
    best_fit_index = 0  # ? 最短路徑出現的代數
    # start = 0  # ? 種群初始位置
    dis_mat = compute_dis_mat(len(citys), coords)  # !
    chroms = greedy_init(dis_mat, len(citys))  # !
    # chroms = init_chromos(start=start, gene_len=len(citys))  # ? 初始化種群

#!-----------------------演化程序-----------------------
    for step in range(max_evolution_num):
        distance_arr = []  # ? 每一染色體的總路線數值
        chroms = choice(citys, chroms)  # ? 選擇
        # chroms = choice_parents(citys, chroms)
        chroms = cross(chroms)  # ? 交配
        chroms = mutation(chroms)  # ? 突變
        # chroms = reverse(citys, chroms)  # ? 染色體反轉
        [distance_arr.append(1.0 / calc_fin_ness(citys, chroms[i]))
         for i in range(len(chroms))]
        best_gens_idx = np.argmin(distance_arr)  # ? 找到最好染色體的位置

        # Score = compute_adp(chroms)  # !

        if distance_arr[best_gens_idx] < min_distance:
            min_distance = distance_arr[best_gens_idx]  # ? 更新最短路徑
            best_gens = chroms[best_gens_idx]  # ? 更新菁英染色體
            if best_fit_index <= step:
                best_fit_index = step + 1
        if step == max_evolution_num - 1:
            start = best_gens[0]
            best_gens.append(start)

        # count = 0
        # m = 0
        # best_chroms = []
        # while m < population_num:
        #     m += 1
        #     if operator.eq(chroms[best_gens_idx], chroms[m-1]) == True:
        #         count += 1
        # if count >= int(population_num*0.7):
        #     best_chroms = chroms[best_gens_idx]
        #     if __name__ == '__main__':
        #         chroms = init_chromos(
        #             start=start, gene_len=len(citys))  # ? 初始化種群
        #         chroms[best_gens_idx] = best_chroms

        draw_H(citys, best_gens)

        print('第{}代：'.format(step + 1), min_distance)

    print('經過{}代的演化，最好的染色體出現在第{}代，其基因為：'.format(
        max_evolution_num, best_fit_index))
    [print(v, end=',' if i < len(best_gens) - 1 else '\n')
     for i, v in enumerate(best_gens)]
    print('最短路徑為：{}'.format(min_distance))
    # draw_H(citys, best_gens)
    plt.ioff()
    plt.show()

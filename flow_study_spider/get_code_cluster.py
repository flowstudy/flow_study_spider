import os
import jieba
from sklearn import manifold
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
import matplotlib.pyplot as plt
#ref:https://www.heywhale.com/mw/project/5f5dc9afae300e0046fdd488


#pip3 install jeiba sklearn wordcloud

def CreatCorpus(path):
    files = os.listdir(path)
    # 读取文档
    text_list = []
    file_list = []
    for file in files:
        if (file[0] == '.'):
            pass
        else:
            with open(os.path.join(path, file), encoding='UTF-8') as f:
                line_list = f.readlines()
            text = ''.join(line for line in line_list)
            text_list.append(text)
            file_list.append(file)

    corpus = []  # 存取430份文档的分词结果
    for text in text_list:
        seg_list = jieba.cut(text, cut_all=True)
        # 对空格，换行符进行处理
        result = []
        for seg in seg_list:
            seg = ''.join(seg.split())
            if (seg != '' and seg != "\n" and seg != "\n\n"):
                result.append(seg)
        # print(result)
        # 将分词后的结果用空格隔开，比如"我来到北京清华大学"，分词结果为："我 来到 北京 清华大学"
        corpus.append(' '.join(result))

    return corpus, file_list

def Tfidf(corpus):
    # 分词向量化
    vectorizer = CountVectorizer(max_df=0.7)
    word_vec = vectorizer.fit_transform(corpus)

    # 提取TF-IDF词向量
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(word_vec)
    tfidf_matrix = tfidf.toarray()  # 对应tfidf矩阵
    # 不同版本的sklearn可能会产生不同的tsne结果，后续聚类等结果会有一定不同
    tsne = manifold.TSNE(n_components=2, perplexity=20.0, early_exaggeration=12.0,
                         learning_rate=200.0, n_iter=1000, init="pca", random_state=0)
    tsne_tfidf_matrix = tsne.fit_transform(tfidf_matrix)
    # print(tsne_tfidf_matrix[:10,:])
    return tsne_tfidf_matrix

def read_text(path, file):
    with open(os.path.join(path, file), encoding='UTF-8') as f:
        line_list = f.readlines()

    # 将文本内容拼接为一个整体文本
    text = ''.join(line for line in line_list)
    return text


def generate_wordclouds(text, out_file):
    # 设置停用词
    stopwords = set(STOPWORDS)
    stopwords.add(r"pub")
    stopwords.add(r"fun")
    stopwords.add(r"let")
    stopwords.add(r"NFT")
    stopwords.add(r"event")



    # stopwords.add(r"weapon")

    # 指定字体为中文
    Words = WordCloud(background_color="white",
                      stopwords=stopwords, width=1200, height=800, margin=2)
    Words.generate(text)

    # 生成词云图
    Words.to_file(out_file)

def kMeans_cluster(tfidf_matrix, path, file_list):
    num_clusters = 2 #8
    km_cluster = KMeans(n_clusters=num_clusters, max_iter=100, n_init=40, \
                        init='k-means++', n_jobs=-1)

    # 返回各自文本的所被分配到的类索引
    labels = km_cluster.fit_predict(tfidf_matrix)

    text_classes = {0: '', 1: '', 2: '', 3: '', 4: '', 5: '', 6: '', 7: ''}
    for k in range(num_clusters):
        text_cls = []
        for file, res in zip(file_list, labels):
            if res == k:
                text = read_text(path, file)
                text_cls.append(text)
        text_join = ''.join(line for line in text_cls)
        text_classes[k] = text_join
        generate_wordclouds(text_join, './' + str(k) + '.png')  # 绘制词云图

    markers = ['^', 'v', '<', '>', 's', 'o', '.', '*']
    colors = ['r', 'g', 'b', 'm', 'k', 'y', 'g', 'r']
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    for i in range(len(labels)):
        plt.scatter(tfidf_matrix[i, 0], tfidf_matrix[i, 1], c=colors[labels[i]], marker=markers[labels[i]])
        plt.text(tfidf_matrix[i, 0], tfidf_matrix[i, 1] + 0.1, '%d' % labels[i], ha='center', va='bottom', fontsize=7)
    fig.savefig('kMeans.png', transparent=False, dpi=600, bbox_inches="tight")
    return labels


def eval_kMeans(X):
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn import metrics
    from sklearn.cluster import KMeans

    # 初始化变量
    scores = []
    values = np.arange(2, 18)

    # 迭代计算不同的轮廓系数值
    for num_clusters in values:
        # 训练kMeans模型
        km_cluster = KMeans(n_clusters=num_clusters, max_iter=100, n_init=40, \
                            init='k-means++', n_jobs=-1)

        km_cluster.fit(tfidf_matrix)
        score = metrics.silhouette_score(X, km_cluster.labels_,
                                         metric='euclidean', sample_size=len(X))

        print("\nNumber of clusters =", num_clusters)
        print("Silhouette score =", score)

        scores.append(score)

    # 输出不同类别个数对应的轮廓系数值
    fig = plt.figure(figsize=(9, 4))
    plt.bar(values, scores, width=0.7, color='b', align='center')
    plt.ylim(0.2, 0.6)
    for a, b in zip(values, scores):
        if a % 2 == 0:
            plt.text(a, b, '%.2f' % b, ha='center', va='bottom', fontsize=10);
    fig.savefig('Silhouette.png', transparent=False, dpi=600, bbox_inches="tight")

    # Extract best score and optimal number of clusters
    num_clusters = np.argmax(scores) + values[0]
    print('\nOptimal number of clusters =', num_clusters)

path = 'code/'
corpus, file_list = CreatCorpus(path)
tfidf_matrix = Tfidf(corpus)

eval_kMeans(tfidf_matrix)
labels = kMeans_cluster(tfidf_matrix, path, file_list)

print(labels)

img = Image.open(os.path.join('./', 'kMeans.png'))

plt.figure(figsize=(20, 16)) # 图像窗口名称
plt.imshow(img)
plt.axis('off') # 关掉坐标轴为 off
plt.title('Cluster Result') # 图像题目
plt.show()



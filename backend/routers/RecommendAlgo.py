import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import NMF
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier

class RecommendAlgo:
    def __init__(self, course_user_matrix):
        self.course_user_matrix = course_user_matrix

    def item_cf(self, user_courses):
        # 计算物品相似度矩阵
        item_similarity = cosine_similarity(self.course_user_matrix)
        #print(item_similarity.shape)
        #print(item_similarity[0])
        item_similarity_df = pd.DataFrame(item_similarity, index=self.course_user_matrix.index, columns=self.course_user_matrix.index)
        #print(item_similarity_df.columns)
        #print(item_similarity_df.shape)
        #print("item", item_similarity_df.head(2))
        # 计算推荐分数
        recommendations = pd.Series(dtype='float64')
        #print("user_courses", user_courses)
        #print("user_courses in or not in", user_courses[0] in item_similarity_df.index)
        for course_id in user_courses:
            if course_id in item_similarity_df.index:
                #print("course_id in similarity_matrix:", course_id)
                sim_scores = item_similarity_df[course_id]
                recommendations = recommendations.add(sim_scores, fill_value=0)
        
        # 排除已选课程
        #print(len(recommendations))
        recommendations = recommendations[~recommendations.index.isin(user_courses)]
        # 将numpy数组转换为pandas Series后再排序
        if isinstance(recommendations, np.ndarray):
            recommendations = pd.Series(recommendations)
        return recommendations.sort_values(ascending=False)

    def matrix_factorization(self, n_components=10):
        # 使用非负矩阵分解进行推荐
        model = NMF(n_components=n_components)
        W = model.fit_transform(self.course_user_matrix)
        H = model.components_
        return np.dot(W, H)

    def logistic_regression_gbdt(self, X, y):
        # 使用Logistic Regression + GBDT进行推荐
        lr = LogisticRegression()
        gbdt = GradientBoostingClassifier()
        
        # 训练模型
        lr.fit(X, y)
        gbdt.fit(X, y)
        
        # 返回预测结果
        return lr.predict_proba(X)[:, 1], gbdt.predict_proba(X)[:, 1]
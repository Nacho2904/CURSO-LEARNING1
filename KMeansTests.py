import unittest
import numpy as np

class KMeans:

    def __init__(self):
        self._centroids = []

    def ProcessSample(self, samples):
        if not samples:
            return np.nan
        else:
            clusters = {index: set() for index in range(0,len(self._centroids))}
            for sample in np.array(samples):
                k_star = np.argmin([np.linalg.norm(sample-centroid) for centroid in self._centroids])
                clusters[k_star].add(sample)

        return clusters



    def Train(self, train_set, K=2, max_iter=10, initial_centroids=[]):
        if not train_set: return []

        if initial_centroids:
            centroids = initial_centroids
        else:
            input_dim = len(train_set[0]) if not str(train_set[0]).isnumeric() else 1
            centroids = np.random.rand(input_dim*K).reshape(K, input_dim)

        clusters = {k: (centroids[k], set()) for k in range(0,K)}

        for iter in range(0,max_iter):
            for input in train_set:
                k = np.argmin(np.array([np.linalg.norm(np.array(input) - np.array(centroid)) for centroid in centroids]))
                clusters[k][1].add(input)

            centroids = [np.sum(np.array(list(clusters[k][1])), axis = 0)/len(clusters[k][1]) for k in range(0,K)]
            clusters = {k: (centroids[k], set()) for k in range(0,K)}

        self._centroids = centroids
        return centroids






class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.KMeanClusters = KMeans()
        self.two_samples_one_dim = [(0), (1)]
        self.many_samples_one_dim = [(0), (1), (0.2), (0.3), (0.8), (0.7), (0.6)]

    def test00KMeanWithNoSamplesReturnsNan(self):
        self.assertTrue(np.isnan(self.KMeanClusters.ProcessSample([])))

    def test01KMeanTrainingWithNoSamplesReturnsEmptyList(self):
        self.assertTrue([] == self.KMeanClusters.Train(train_set=[], K=2))

    def test02KMeanTrainingWithTwoSamplesAndTwoClustersReturnsTwoCentroids(self):
        self.assertTrue(len(self.KMeanClusters.Train(train_set = self.two_samples_one_dim, K=2)) == 2)

    def test03KMeanTrainingWithTwoSamplesAndTwoClustersReturnsTheCorrectCentroids(self):
        # Here and above I'll manually set the initial centroids to [0.1,0.7]
        self.assertTrue(self.KMeanClusters.Train(train_set=self.two_samples_one_dim, K=2, initial_centroids=[(0.1),(0.7)]) == [(0),(1)])

    def test04KMeanProcessClassifiesTwoExamplesToTheCorrectClusterAfterBeingTrainedWithTwoSamplesForTwoClasses(self):
        self.KMeanClusters.Train(train_set=self.two_samples_one_dim, K=2, initial_centroids=[(0.1),(0.7)])
        predicted_clusters = self.KMeanClusters.ProcessSample(samples=[0.2,0.8])
        self.assertTrue(predicted_clusters == {0: {0.2}, 1: {0.8}})

    def test05KMeanTrainingWithNSamplesAndTwoClustersReturnsTheCorrectCentroids(self):
        predicted_centroids = self.KMeanClusters.Train(train_set=self.many_samples_one_dim, K=2, initial_centroids=[(0.1),(0.7)])
        self.assertTrue(all(np.isclose(np.array(predicted_centroids), np.array([1/6, 0.775]))))

    def test06KMeanTrainingWithTwoTwoDimensionalSamplesReturnsTheCorrectCentroids(self):
        predicted_centroids = self.KMeanClusters.Train(train_set=[(1,1), (0,0)], K=2, initial_centroids = [(0.1,0.2), (1.1, 0.9)])
        self.assertTrue(np.all(np.isclose(np.array(predicted_centroids), np.array([(0, 0), (1, 1)]))))

    def test07KMeanTrainingCanBeInitializedWithoutManuallySettingTheInitialCentroids(self):
        predicted_centroids = self.KMeanClusters.Train(train_set=[(1,1), (0,0)], K=2, max_iter=100)
        self.assertTrue(np.all(np.isclose(np.array(predicted_centroids), np.array([(1, 1), (0, 0)])))
                        or np.all(np.isclose(np.array(predicted_centroids), np.array([(0, 0), (1, 1)]))))


if __name__ == '__main__':
    unittest.main()

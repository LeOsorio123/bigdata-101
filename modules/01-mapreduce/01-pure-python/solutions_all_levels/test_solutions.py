"""Standard-library tests for all twelve functional exercises."""
import unittest
from common import mapreduce,source_files,lines_from_files
import level1 as a
import level2 as b
import level3 as c
class SolutionTests(unittest.TestCase):
    def test_1_1(self):
        self.assertEqual(mapreduce(['Aa! b'],a.character_mapper,a.sum_values),{'a':2,'b':1})
        self.assertEqual(mapreduce([],a.character_mapper,a.sum_values),{})
    def test_1_2(self):
        self.assertEqual(mapreduce(['Apple programming, bigdata!'],a.long_words_mapper,a.sum_values),{'programming':1,'bigdata':1})
    def test_1_3(self):
        self.assertEqual(mapreduce(a.SALES,a.product_mapper,a.mean_reducer)['Laptop'],1183.3)
    def test_1_4(self):
        self.assertEqual(mapreduce(a.TEMPS,a.temp_mapper,a.temp_reducer)['Bogota'],{'min':13,'max':15,'avg':14.0})
    def test_1_5(self):
        self.assertEqual(mapreduce(a.CATEGORIES,a.category_mapper,a.category_reducer)['Electronics'],{'count':3,'total':1675,'avg':558.3})
    def test_2_1(self):
        self.assertEqual(mapreduce(['A an abc!'],b.length_mapper,b.sum_reducer),{1:1,2:1,3:1})
    def test_2_2(self):
        self.assertEqual(mapreduce([('a.txt','Cat cat dog'),('b.txt','CAT')],b.file_word_mapper,b.unique_reducer),{'a.txt':2,'b.txt':1})
    def test_2_3(self):
        self.assertEqual(mapreduce([('a.txt','cat cat'),('b.txt','cat dog')],b.index_mapper,b.index_reducer),{'cat':['a.txt','b.txt'],'dog':['b.txt']})
    def test_files_present(self):
        self.assertTrue(source_files())
        self.assertTrue(list(lines_from_files(source_files())))
    def test_3_1(self):
        self.assertEqual(c.top_n_words(['x x y'],1),[('x',2)])
        self.assertEqual(c.top_n_words([],10),[])
        self.assertEqual(c.top_n_words(['x'],0),[])
    def test_3_2(self):
        self.assertEqual(mapreduce(c.TEXT,c.bigram_mapper,c.sum_reducer)['the quick'],2)
        self.assertEqual(mapreduce(['single'],c.bigram_mapper,c.sum_reducer),{})
    def test_3_3(self):
        self.assertEqual(mapreduce(c.EVENTS,c.event_mapper,c.event_reducer)['U1'],{'page_views':3,'unique_pages':['/cart','/home','/products']})
    def test_3_4(self):
        result=mapreduce(c.READINGS,c.sensor_mapper,c.sensor_reducer)
        self.assertAlmostEqual(result['S1']['avg'],48.47,2)
        self.assertEqual(result['S1']['anomalies'],[])
        self.assertEqual(mapreduce([{'sensor':'Z','value':7}],c.sensor_mapper,c.sensor_reducer)['Z']['std_dev'],0)
if __name__=='__main__':unittest.main(verbosity=2)


import sys, os, unittest
from collections import defaultdict
sys.path.append(os.path.join(os.path.dirname(__file__), '../data_generator/'))

from data_generator import merge_dict_lists, flush_to_disk, buffered_write_to_disk, write_log_entry

test_log_file = 'test_log.txt'
test_watch_movie_file = 'test_watch_movie.txt'
test_recommend_movie_file = 'test_recommend_movie.txt'

test_entries = [
    '2024-02-27T18:45:18,156972,GET /data/m/batman+begins+2005/91.mpg',
    '2024-02-27T18:45:18,379040,GET /data/m/a+matter+of+life+and+death+1946/88.mpg',
    '2024-02-27T18:45:18,394870,GET /data/m/his+girl+friday+1940/85.mpg',
    '2024-02-27T18:45:18.198010,145051,recommendation request 17645-team05.isri.cmu.edu:8082, status 200, result: rashomon+1950, the+apartment+1960, his+girl+friday+1940, the+shawshank+redemption+1994, buena+vista+social+club+1999, princess+mononoke+1997, in+the+mood+for+love+2000, bob+roberts+1992, the+godfather+1972, harry+potter+and+the+deathly+hallows+part+2+2011, witness+for+the+prosecution+1957, my+neighbor+totoro+1988, little+big+man+1970, the+triplets+of+belleville+2003, the+400+blows+1959, the+seventh+seal+1957, castle+in+the+sky+1986, schindlers+list+1993, m+1931, paths+of+glory+1957, 140 ms',
    '2024-02-27T18:45:18.249072,241611,recommendation request 17645-team05.isri.cmu.edu:8082, status 200, result: rashomon+1950, the+apartment+1960, his+girl+friday+1940, the+shawshank+redemption+1994, buena+vista+social+club+1999, princess+mononoke+1997, in+the+mood+for+love+2000, bob+roberts+1992, the+godfather+1972, harry+potter+and+the+deathly+hallows+part+2+2011, witness+for+the+prosecution+1957, my+neighbor+totoro+1988, little+big+man+1970, the+triplets+of+belleville+2003, the+400+blows+1959, the+seventh+seal+1957, castle+in+the+sky+1986, schindlers+list+1993, m+1931, paths+of+glory+1957, 185 ms'
]


def convert_to_dict(records):
    return {i.split(",")[0]: set([j.strip() for j in i.split(",")[1:]]) for i in records}

class TestDataGenerator(unittest.TestCase):
        
    def test_merge_dict_lists_empty_key_match(self):
        dict_a = {'a': set([1, 2, 3]), 'b': set([4, 5, 6])}
        dict_b = {'a': set([7, 8, 9]), 'd': set([10, 11, 12])}
        merge_dict_lists(dict_a, dict_b)
        self.assertEqual(dict_a['a'], set([1, 2, 3, 7, 8, 9]))
        self.assertEqual(dict_a['b'], set([4, 5, 6]))
        self.assertEqual(dict_a['d'], set([10, 11, 12]))
        
    def test_merge_dict_lists_empty_no_key_match(self):
        dict_a = {'a': set([1, 2, 3]), 'b': set([4, 5, 6])}
        dict_b = {'c': set([7, 8, 9]), 'd': set([10, 11, 12])}
        merge_dict_lists(dict_a, dict_b)
        self.assertEqual(dict_a['a'], set([1, 2, 3]))
        self.assertEqual(dict_a['b'], set([4, 5, 6]))
        self.assertEqual(dict_a['c'], set([7, 8, 9]))
        self.assertEqual(dict_a['d'], set([10, 11, 12]))
    
    def test_buffered_write_to_disk(self):
        if os.path.exists(test_log_file):
            os.remove(test_log_file)
        buffer = []
        buffer.append("line1" + "\n")
        buffer.append("line2" + "\n")
        buffer.append("line3" + "\n")
        buffered_write_to_disk(test_log_file, buffer)
        with open(test_log_file, 'r') as file:
            result = file.readlines()
        self.assertEqual(result, ["line1\n", "line2\n", "line3\n"])
        self.assertEqual(buffer, [])
        if os.path.exists(test_log_file):
            os.remove(test_log_file)
    
    def test_flush_to_disk_first_time(self):
        if os.path.exists(test_watch_movie_file):
            os.remove(test_watch_movie_file)
        dict = {'a': set(["1", "2", "3"]), 'b': set(["4", "5", "6"])}
        flush_to_disk(test_watch_movie_file, dict)
        with open(test_watch_movie_file, 'r') as file:
            result = file.readlines()
        new_dict = convert_to_dict(result)
        self.assertEqual(new_dict, dict)
        if os.path.exists(test_watch_movie_file):
            os.remove(test_watch_movie_file)    
    
    def test_flush_to_disk_not_first_time(self):
        if os.path.exists(test_watch_movie_file):
            os.remove(test_watch_movie_file)
        old_dict = {'a': set(["1", "2", "3"]), 'b': set(["4", "5", "6"])}
        flush_to_disk(test_watch_movie_file, old_dict)
        new_dict = {'a': set(["7", "8", "9"]), 'd': set(["10", "11", "12"])}
        flush_to_disk(test_watch_movie_file, new_dict)
        merge_dict_lists(old_dict, new_dict)
        with open(test_watch_movie_file, 'r') as file:
            result = file.readlines()
        result = convert_to_dict(result)
        self.assertEqual(result, old_dict)
        if os.path.exists(test_watch_movie_file):
            os.remove(test_watch_movie_file)   
    
    def test_write_log_entry(self):
        watched = defaultdict(set)
        recommended = defaultdict(set)
        correct_watched = {
            '156972': set(['batman+begins+2005']),
            '379040': set(['a+matter+of+life+and+death+1946']),
            '394870' : set(['his+girl+friday+1940'])
        }
        correct_recommended = {
            '145051': {'the+400+blows+1959', 'schindlers+list+1993', 'castle+in+the+sky+1986', 'the+triplets+of+belleville+2003', 'witness+for+the+prosecution+1957', 'the+apartment+1960', 'bob+roberts+1992', 'in+the+mood+for+love+2000', 'the+godfather+1972', 'little+big+man+1970', 'buena+vista+social+club+1999', 'princess+mononoke+1997', 'the+seventh+seal+1957', 'm+1931', 'my+neighbor+totoro+1988', 'paths+of+glory+1957', 'the+shawshank+redemption+1994', 'rashomon+1950', 'harry+potter+and+the+deathly+hallows+part+2+2011', 'his+girl+friday+1940'},
            '241611' : {'the+400+blows+1959', 'schindlers+list+1993', 'castle+in+the+sky+1986', 'the+triplets+of+belleville+2003', 'witness+for+the+prosecution+1957', 'the+apartment+1960', 'bob+roberts+1992', 'in+the+mood+for+love+2000', 'the+godfather+1972', 'little+big+man+1970', 'buena+vista+social+club+1999', 'princess+mononoke+1997', 'the+seventh+seal+1957', 'm+1931', 'my+neighbor+totoro+1988', 'paths+of+glory+1957', 'the+shawshank+redemption+1994', 'rashomon+1950', 'harry+potter+and+the+deathly+hallows+part+2+2011', 'his+girl+friday+1940'}
        }
            
        for entry in test_entries:
            write_log_entry(entry, 'N', 0, watched, recommended)
        self.assertEqual(watched, correct_watched)
        self.assertEqual(recommended, correct_recommended)
        
if __name__ == '__main__':
    unittest.main()

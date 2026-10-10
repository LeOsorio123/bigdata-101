"""Level 3: top-N words, bigrams, user sessions and sensor readings."""
import math
from common import mapreduce, words
TEXT=['the quick brown fox','the quick red dog']
EVENTS=[{'user':'U1','page':'/home','time':'10:00'},{'user':'U1','page':'/products','time':'10:02'},{'user':'U2','page':'/home','time':'10:01'},{'user':'U1','page':'/cart','time':'10:05'},{'user':'U2','page':'/about','time':'10:03'}]
READINGS=[{'sensor':'S1','value':22.5},{'sensor':'S1','value':23.0},{'sensor':'S1','value':99.9},{'sensor':'S2','value':15.0},{'sensor':'S2','value':14.8}]
def word_mapper(line):
    for word in words(line): yield word,1
def sum_reducer(key,values): return sum(values)
def top_n_words(lines,n=10):
    if n<=0:return []
    return sorted(mapreduce(lines,word_mapper,sum_reducer).items(),key=lambda item:(-item[1],item[0]))[:n]
def bigram_mapper(line):
    tokens=words(line)
    for i in range(len(tokens)-1):yield f'{tokens[i]} {tokens[i+1]}',1
def event_mapper(event):yield event['user'],event['page']
def event_reducer(user,pages):return {'page_views':len(pages),'unique_pages':sorted(set(pages))}
def sensor_mapper(record):yield record['sensor'],record['value']
def sensor_reducer(sensor,values):
    avg=sum(values)/len(values)
    std=math.sqrt(sum((value-avg)**2 for value in values)/len(values))
    return {'avg':round(avg,2),'std_dev':round(std,2),'anomalies':[value for value in values if abs(value-avg)>2*std]}
def main():
    print('3.1 Top N:',top_n_words(TEXT,10))
    print('3.2 Bigrams:',mapreduce(TEXT,bigram_mapper,sum_reducer))
    print('3.3 Sessions:',mapreduce(EVENTS,event_mapper,event_reducer))
    print('3.4 Anomalies:',mapreduce(READINGS,sensor_mapper,sensor_reducer))
    print('Note: three values cannot exceed 2 population standard deviations.')
if __name__=='__main__':main()

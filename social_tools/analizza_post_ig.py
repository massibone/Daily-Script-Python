import pandas as pd
from collections import Counter
import re


def analizza_performance(csv_file):
    df = pd.read_csv(csv_file)  # Colonne: 'caption', 'likes', 'comments', 'hashtags'
    
    # Estrai hashtag da caption
    df['hashtags_list'] = df['caption'].apply(lambda x: re.findall(r'#\w+', str(x).lower()))
    
    # Pesa hashtag per engagement (likes + comments * 2)
    df['engagement'] = df['likes'] + df['comments'] * 2
    hashtag_engagement = []
    for idx, row in df.iterrows():
        for tag in row['hashtags_list']:
            hashtag_engagement.append((tag, row['engagement']))
    
    top_hashtag = Counter(hashtag_engagement).most_common(10)
    return pd.DataFrame(top_hashtag, columns=['hashtag', 'total_engagement'])

# Esempio
risultati = analizza_performance('miei_post_ig.csv')
print(risultati)
# Output: hashtag | total_engagement
# #streetphotography | 1250

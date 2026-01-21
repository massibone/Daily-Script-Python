
'''
NP CORRELATION CORRCOEF
The code to print out the mean height is already included. 
Complete the code for the median height. 
'''

# Import numpy
import numpy as np


# Print mean height (first column)
avg = np.mean(np_baseball[:,0])
print("Average: " + str(avg))


# Print median height. Replace 'None'
med = np.median(np_baseball[:,0])
print("Median: " + str(med))


# Print out the standard deviation on height. Replace 'None'
stddev = np.std(np_baseball[:,0])
print("Standard Deviation: " + str(stddev))


# Print out correlation between first and second column. Replace 'None'
corr = np.corrcoef(np_baseball[:,0],np_baseball[:,1])
print("Correlation: " + str(corr))
'''
RISULTATO
<script.py> output:
    Average: 73.6896551724
    Median: 74.0
    Standard Deviation: 2.31279188105
    Correlation: [[ 1.          0.53153932]
     [ 0.53153932  1.        ]]
'''


import scapy.all as scapy
import pandas as pd
from sklearn.ensemble import IsolationForest

def packet_features(pkt):
    # Estrai features semplici dal pacchetto (esempio)
    return {
        'src': pkt[0][1].src,
        'dst': pkt[0][1].dst,
        'len': len(pkt),
        'proto': pkt[0][1].proto
    }


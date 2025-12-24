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

def capture_packets(num=500):
    packets = scapy.sniff(count=num)
    features = [packet_features(pkt) for pkt in packets if pkt.haslayer(scapy.IP)]
    return pd.DataFrame(features)

def detect_anomalies(df):
    clf = IsolationForest(random_state=42)
    X = df[['len', 'proto']]
    preds = clf.fit_predict(X)
    df['anomaly'] = preds
    return df[df['anomaly'] == -1]  # Solo gli anomali

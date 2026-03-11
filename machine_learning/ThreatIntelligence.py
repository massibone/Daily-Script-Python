'''
pipeline minima di classificazione phishing testi
Esempio base di vettorializzazione testo, classificazione con RandomForest basata su frasi esempio di email phishing e non
'''
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

# Dati demo: esempi testuali phishing (1) e legittimi (0)
texts = [
    "Urgent: update your account details",         # phishing
    "Your invoice is attached",                     # legittimo
    "Verify your password immediately",             # phishing
    "Meeting schedule confirmed",                    # legittimo
    "Click here for prize money",                    # phishing
    "Project report attached",                       # legittimo
]
labels = [1, 0, 1, 0, 1, 0]

# Vettorializzazione testo
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

# Classificatore RF
clf = RandomForestClassifier(random_state=42)
clf.fit(X, labels)

# Nuovo testo da classificare
new_emails = ["Hurry, verify your account now", "Lunch tomorrow at 12"]
X_new = vectorizer.transform(new_emails)
pred = clf.predict(X_new)

for email, p in zip(new_emails, pred):
    print(f"'{email}' => {'Phishing' if p else 'Legittimo'}")


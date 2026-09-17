LDPC (Low-Density Parity-Check)

Implementazione in Python di un codice LDPC: costruzione della matrice di parità, codifica sistematica, trasmissione su canale rumoroso (BSC) e decodifica con belief propagation (sum-product).

Cosa fa
LDPC(N, K, weight_row, weight_col, seed) costruisce un codice con parola di codice lunga N e messaggio lungo K.
encode(message) produce un codeword sistematico [message | parity].
decode(received, error_prob, max_iterations) recupera il messaggio da una parola ricevuta con errori, tramite belief propagation, e ritorna anche converged (bool) per sapere se la decodifica ha davvero trovato una parola valida.
run_trials(...) esegue più trasmissioni simulate e stampa il bit error rate (BER) medio e la percentuale di decodifiche convergenti.

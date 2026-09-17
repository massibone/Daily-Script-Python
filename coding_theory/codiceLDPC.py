"""
Implementazione didattica di un codice LDPC (Low-Density Parity-Check).

Versione revisionata rispetto alla bozza originale. Le modifiche principali
sono spiegate nel README.md allegato; qui in breve i punti chiave:

1. La matrice H viene costruita direttamente in forma sistematica H = [A | I_M].
   Questo garantisce che H sia sempre coerente con la codifica sistematica
   usata in encode() (bug presente nella versione originale: la parte destra
   di H era generata a caso e quasi mai coincideva con l'identita', quindi
   il codeword prodotto non soddisfaceva H . codeword = 0).
2. La costruzione di A usa un "configuration model" (socket model) per
   ottenere pesi di riga e di colonna il piu' possibile vicini ai target,
   evitando il fix-up post-hoc della versione originale che rompeva i pesi
   di riga gia' assegnati.
3. decode() implementa una vera sum-product belief propagation a livello di
   arco (messaggi check->var e var->check separati), con esclusione del
   contributo della variabile stessa (messaggio estrinseco) e con le
   probabilita' iniziali calibrate sulla error_prob reale del canale invece
   di valori fissi 0.9/0.1.
4. decode() restituisce anche un flag di convergenza, invece di restituire
   silenziosamente un risultato non validato quando la sindrome non si
   annulla entro max_iterations.
"""

import numpy as np
from scipy.sparse import csr_matrix


class LDPC:
    def __init__(self, N, K, weight_row=3, weight_col=6, seed=None):
        """
        N: lunghezza della parola di codice
        K: lunghezza del messaggio
        weight_row: peso "target" di ogni riga nella sotto-matrice A (M x K)
        weight_col: peso "target" di ogni colonna messaggio nella sotto-matrice A
        seed: seme per il generatore casuale (per riproducibilita')
        """
        self.N = N
        self.K = K
        self.M = N - K
        self.weight_row = weight_row
        self.weight_col = weight_col
        self.rng = np.random.default_rng(seed)

        # H = [A | I_M]: A ha dimensione M x K, I_M e' l'identita' M x M.
        # Il peso di riga complessivo di H e' quindi weight_row + 1 (il bit
        # extra dell'identita'), il peso delle colonne di parita' e' 1 per
        # costruzione: e' il prezzo di avere una forma sistematica semplice
        # e sempre coerente, vedi README.
        self.A = self._generate_A()
        self.H = csr_matrix(np.hstack([self.A, np.eye(self.M, dtype=int)]))

    def _generate_A(self):
        """
        Genera la sotto-matrice A (M x K) con un configuration model:
        crea 'socket' di riga (M righe x weight_row) e 'socket' di colonna
        (K colonne x weight_col), li accoppia casualmente ed elimina i
        doppioni. Il peso finale puo' scostarsi leggermente dal target se K
        e M sono piccoli, ma senza rompere i pesi gia' assegnati come nella
        versione originale.
        """
        A = np.zeros((self.M, self.K), dtype=int)

        row_sockets = np.repeat(np.arange(self.M), self.weight_row)
        col_sockets = np.repeat(np.arange(self.K), self.weight_col)

        # Se i totali non combaciano (M*weight_row != K*weight_col), si
        # tronca il piu' lungo: e' una scelta esplicita e documentata,
        # non un fix-up nascosto.
        n_edges = min(len(row_sockets), len(col_sockets))
        self.rng.shuffle(row_sockets)
        self.rng.shuffle(col_sockets)
        row_sockets = row_sockets[:n_edges]
        col_sockets = col_sockets[:n_edges]

        for r, c in zip(row_sockets, col_sockets):
            A[r, c] = 1  # eventuali doppioni collassano semplicemente a 1

        # Evita righe o colonne completamente a zero (renderebbero quella
        # equazione di parita' o quel bit messaggio "invisibile" al codice).
        for r in range(self.M):
            if A[r].sum() == 0:
                c = self.rng.integers(0, self.K)
                A[r, c] = 1
        for c in range(self.K):
            if A[:, c].sum() == 0:
                r = self.rng.integers(0, self.M)
                A[r, c] = 1

        return A

    def encode(self, message):
        """
        Codifica sistematica: codeword = [message | parity], con
        parity[i] = XOR dei bit messaggio selezionati dalla riga i di A.
        Per costruzione soddisfa sempre H . codeword = 0 (mod 2).
        """
        message = np.asarray(message, dtype=int) % 2
        if len(message) != self.K:
            raise ValueError(f"Il messaggio deve essere lungo {self.K} bit")

        parity = (self.A @ message) % 2
        codeword = np.concatenate([message, parity])
        return codeword

    def decode(self, received, error_prob=0.05, max_iterations=50):
        """
        Decodifica con sum-product belief propagation (messaggi per arco).
        received: vettore 0/1 (eventualmente con errori)
        error_prob: probabilita' di crossover del canale, usata per
                    calibrare le log-likelihood ratio iniziali
        Ritorna (messaggio_decodificato, convergenza: bool)
        """
        received = np.asarray(received, dtype=int)
        p = min(max(error_prob, 1e-6), 0.5 - 1e-6)  # evita log(0)/divisioni

        # LLR iniziale per ogni bit: positivo => piu' probabile 0, negativo => piu' probabile 1
        llr_ch = np.where(received == 0, np.log((1 - p) / p), -np.log((1 - p) / p))

        rows, cols = self.H.nonzero()
        edges = list(zip(rows.tolist(), cols.tolist()))

        # messaggi var->check e check->var, indicizzati per arco
        m_v2c = {(v, c): llr_ch[v] for (c, v) in edges}
        m_c2v = {(c, v): 0.0 for (c, v) in edges}

        checks_of_var = {}
        vars_of_check = {}
        for c, v in edges:
            checks_of_var.setdefault(v, []).append(c)
            vars_of_check.setdefault(c, []).append(v)

        converged = False
        decoded = (llr_ch < 0).astype(int)

        for _ in range(max_iterations):
            # --- aggiornamento nodi di controllo (check node) ---
            for c, vs in vars_of_check.items():
                tanh_vals = {v: np.tanh(m_v2c[(v, c)] / 2) for v in vs}
                for v in vs:
                    prod = 1.0
                    for v2 in vs:
                        if v2 != v:
                            prod *= tanh_vals[v2]
                    prod = np.clip(prod, -1 + 1e-9, 1 - 1e-9)
                    m_c2v[(c, v)] = 2 * np.arctanh(prod)

            # --- aggiornamento nodi variabile (variable node) ---
            total_llr = llr_ch.copy()
            for v, cs in checks_of_var.items():
                total_llr[v] += sum(m_c2v[(c, v)] for c in cs)
                for c in cs:
                    m_v2c[(v, c)] = total_llr[v] - m_c2v[(c, v)]

            decoded = (total_llr < 0).astype(int)
            syndrome = self.H.dot(decoded) % 2
            if np.all(syndrome == 0):
                converged = True
                break

        return decoded[: self.K], converged


def simulate_transmission(codeword, error_prob, rng):
    """Simula un canale binario simmetrico (BSC) con probabilita' error_prob."""
    received = codeword.copy()
    errors = rng.random(len(codeword)) < error_prob
    received[errors] = 1 - received[errors]
    return received


def run_trials(N=20, K=10, error_prob=0.05, n_trials=200, seed=0):
    """
    Esegue piu' trial indipendenti e stampa il bit error rate (BER) medio
    e la frazione di decodifiche convergenti, invece di mostrare un singolo
    run "fortunato" come nella versione originale.
    """
    rng = np.random.default_rng(seed)
    ldpc = LDPC(N, K, seed=seed)

    total_bit_errors = 0
    total_bits = 0
    n_converged = 0

    for _ in range(n_trials):
        message = rng.integers(0, 2, K)
        codeword = ldpc.encode(message)
        received = simulate_transmission(codeword, error_prob, rng)
        decoded, converged = ldpc.decode(received, error_prob=error_prob)

        total_bit_errors += np.sum(message != decoded)
        total_bits += K
        n_converged += int(converged)

    ber = total_bit_errors / total_bits
    print(f"N={N}, K={K}, error_prob={error_prob}, trial={n_trials}")
    print(f"BER medio: {ber:.4f}")
    print(f"Decodifiche convergenti: {n_converged}/{n_trials}")


if __name__ == "__main__":
    run_trials()

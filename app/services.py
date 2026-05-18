from pathlib import Path
import json
import os
import unicodedata
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent


USE_RERANKER = os.environ.get("POKEIA_USE_RERANKER", "0") == "1"
RERANKER_MODEL = os.environ.get(
    "POKEIA_RERANKER_MODEL", "BAAI/bge-reranker-v2-m3"
)



TYPE_HINTS = {
    "fire":     {"fogo", "chamas", "flama", "fire", "flame", "burning", "incendio", "queimadura"},
    "water":    {"agua", "aquatico", "mar", "oceano", "rio", "water", "aquatic", "marinho", "submarino"},
    "grass":    {"planta", "grama", "natureza", "vegetal", "grass", "plant", "floresta", "botanico"},
    "electric": {"eletrico", "raio", "raios", "eletrica", "relampago", "trovao", "electric", "thunder", "lightning"},
    "psychic":  {"psiquico", "mental", "telepatia", "telecinese", "psychic", "mente"},
    # dark = sinistro + predador noturno + monstro agressivo
    "dark":     {"sombrio", "sombrios", "escuro", "trevas", "noturno", "maligno",
                 "dark", "sinister", "evil", "perverso",
                 "predador", "predadores", "predadora",
                 "agressivo", "agressivos", "agressiva", "agressivas",
                 "monstro", "monstros", "monstruoso", "monstruosa",
                 "perigoso", "perigosos", "perigosa", "perigosas",
                 "destrutivo", "destrutivos", "destrutiva"},
    "fairy":    {"fada", "fadas", "magico", "magicos", "encantado", "encantados",
                 "fofo", "fofos", "fofa", "fofinhos",
                 "adoravel", "adoraveis",
                 "fairy", "magical", "enchanted", "cute", "adorable", "lovely",
                 "encantador", "encantadora",
                 "pequeno", "pequenos", "pequenina", "tiny", "small", "little"},
    "dragon":   {"dragao", "dragoes", "draconico", "serpente", "dragon", "draconic"},
    # ghost = espectral + medo/pesadelo + triste/melancolico/abandonado
    "ghost":    {"fantasma", "fantasmas", "espectro", "espirito", "espirito",
                 "assombracao", "morto", "alma", "almas",
                 "ghost", "spectral", "haunting", "haunted",
                 "pesadelo", "pesadelos", "horror", "medo", "terror",
                 "assustador", "scary", "nightmare", "nightmares",
                 "triste", "tristes",
                 "solitario", "solitarios", "solitaria",
                 "melancolico", "melancolicos", "melancolica",
                 "abandonado", "abandonados", "abandonada",
                 "esquecido", "esquecidos", "sad", "lonely", "abandoned",
                 "amaldicoado", "cursed"},
    "steel":    {"aco", "metal", "metalico", "metalicos",
                 "robotico", "roboticos", "robotica",
                 "robos", "robo", "robotic", "machine", "machines", "mechanical",
                 "maquina", "maquinas",
                 "artificial", "artificiais", "tecnologia", "tecnologico",
                 "cyborg", "android", "automato"},
    "fighting": {"lutador", "lutadores", "lutadora", "marcial", "combate", "luta",
                 "guerreiro", "guerreiros", "samurai", "samurais",
                 "fighting", "warrior", "fighter", "ninja", "ninjas"},
    "poison":   {"veneno", "venenoso", "venenosos", "toxico", "toxicos",
                 "poison", "venom", "toxic", "peconha"},
    "ground":   {"terra", "solo", "subterraneo", "ground", "earth", "deserto"},
    "rock":     {"rocha", "pedra", "mineral",
                 "fossil", "fosseis", "fossilizado", "ancestral",
                 "prehistorico", "prehistoricos",
                 "antigo", "antigos", "extinto", "extintos",
                 "rock", "stone", "ancient", "prehistoric", "extinct"},
    "ice":      {"gelo", "gelado", "frio", "congelante", "neve", "ice", "frozen", "cold", "glacial"},
    "flying":   {"voador", "voadora", "voadores", "voadoras",
                 "asas", "asa", "voa", "voam", "voando",
                 "aereo", "ceu", "ave", "aves",
                 "flying", "winged", "fly", "flies", "bird", "birds",
                 "alado", "alados", "alada"},
    "bug":      {"inseto", "insetos", "besouro", "besouros", "borboleta", "aranha",
                 "bug", "insect", "insects", "spider"},
    "normal":   set(),  # "normal" é ambíguo demais para boost
}


PT_TO_EN_GLOSSARY = {
    # tipos
    "fogo": "fire flame burning", "água": "water sea ocean aquatic",
    "agua": "water sea ocean aquatic", "planta": "grass plant nature",
    "elétrico": "electric thunder lightning", "eletrico": "electric thunder lightning",
    "psíquico": "psychic mind telepathic", "psiquico": "psychic mind telepathic",
    "sombrio": "dark sinister evil", "fada": "fairy magical enchanted",
    "dragão": "dragon", "dragao": "dragon", "dragões": "dragon",
    "fantasma": "ghost spectral haunting", "fantasmas": "ghost spectral haunting",
    "aço": "steel metal", "aco": "steel metal",
    "lutador": "fighting martial warrior", "lutadores": "fighting martial warrior",
    "veneno": "poison venom toxic", "venenoso": "poison venom toxic",
    "terra": "ground earth soil", "rocha": "rock stone",
    "gelo": "ice frozen cold", "voador": "flying bird winged",
    "voadores": "flying bird winged", "voa": "flying flies fly winged",
    "inseto": "bug insect", "insetos": "bug insect",
    # conceitos abstratos
    "deuses": "gods divine deity creator", "deus": "god divine deity creator",
    "divindades": "divine deity gods", "divindade": "divine deity god",
    "criadores": "creator divine god", "criador": "creator divine god",
    "universo": "universe cosmos", "cosmos": "cosmos space stars",
    "espaço": "space cosmos stars", "espaco": "space cosmos stars",
    "estrelas": "stars stellar", "lua": "moon lunar", "sol": "sun solar",
    "lendário": "legendary mythical", "lendarios": "legendary mythical",
    "lendários": "legendary mythical", "mítico": "mythical legendary",
    "tristes": "sad lonely melancholic", "triste": "sad lonely melancholic",
    "solitário": "lonely solitary alone", "solitarios": "lonely solitary alone",
    "solitários": "lonely solitary alone",
    "melancólicos": "melancholic sad sorrowful",
    "melancolicos": "melancholic sad sorrowful",
    "abandonados": "abandoned forgotten",
    "fofos": "cute adorable", "fofo": "cute adorable",
    "fofinhos": "cute adorable",
    "pequenos": "small tiny little", "pequeno": "small tiny little",
    "adoráveis": "adorable cute lovely", "adoraveis": "adorable cute lovely",
    "mágicos": "magical mystical", "magicos": "magical mystical",
    "encantados": "enchanted magical", "fósseis": "fossil prehistoric ancient",
    "fosseis": "fossil prehistoric ancient",
    "fóssil": "fossil prehistoric ancient",
    "fossil": "fossil prehistoric ancient",
    "pré-históricos": "prehistoric ancient extinct",
    "pré-historicos": "prehistoric ancient extinct",
    "prehistoricos": "prehistoric ancient extinct",
    "antigos": "ancient old", "extintos": "extinct prehistoric",
    "predadores": "predator hunter dangerous",
    "perigosos": "dangerous deadly threatening",
    "agressivos": "aggressive ferocious violent",
    "destrutivos": "destructive devastating",
    "monstros": "monster creature beast",
    "pesadelos": "nightmare horror", "pesadelo": "nightmare horror",
    "medo": "fear scary frightening", "horror": "horror terror scary",
    "assombração": "haunting ghost specter",
    "assombracao": "haunting ghost specter",
    "terror": "terror horror scary",
    "robóticos": "robotic mechanical machine artificial",
    "roboticos": "robotic mechanical machine artificial",
    "mecânicos": "mechanical machine robotic", "mecanicos": "mechanical machine robotic",
    "artificiais": "artificial synthetic man-made",
    "máquinas": "machine robot mechanical", "maquinas": "machine robot mechanical",
    "tecnologia": "technology technological mechanical",
    "mitologia": "mythology myth folklore legend",
    "japonesa": "japanese japan oriental",
    "japonês": "japanese japan oriental", "japones": "japanese japan oriental",
    "lendas": "legends mythology folklore", "lenda": "legend mythology folklore",
    "orientais": "oriental eastern asian", "oriental": "oriental eastern asian",
    "samurai": "samurai katana warrior sword",
    "samurais": "samurai katana warrior",
    "ninja": "ninja shinobi shadow assassin",
    "ninjas": "ninja shinobi shadow",
    "raposa": "fox kitsune", "raposas": "fox kitsune",
    "raposinha": "fox kitsune",
    "parecem": "look like resembling similar to",
    "parecidos": "similar resembling like",
    "inspirados": "inspired based on",
    "inspirado": "inspired based on",
    "relacionados": "related connected linked",
    "que voa": "that flies flying winged",
    "que voam": "that fly flying winged",
    "voam": "fly flying winged",
    "oceano": "ocean sea deep waters",
    "mar": "sea ocean", "marinho": "marine sea ocean",
    "profundo": "deep abyssal", "profundezas": "deep abyssal depths",
    "rápidos": "fast quick swift speedy",
    "rapidos": "fast quick swift speedy",
    "rápido": "fast quick swift speedy",
    "rapido": "fast quick swift speedy",
    "velozes": "fast swift quick",
    "veloz": "fast swift quick",
    "raio": "lightning thunder",
    "raios": "lightning thunder",
    "relâmpago": "lightning thunder",
    "relampago": "lightning thunder",
}


def expand_query_pt_en(query: str) -> str:
    """Concatena query original com tradução leve PT→EN (não destrutiva)."""
    q_lower = query.lower()
    q_norm = unicodedata.normalize('NFKD', q_lower)
    q_norm = ''.join(c for c in q_norm if not unicodedata.combining(c))
    extras = []
    # tenta casar multi-palavra primeiro
    for key in sorted(PT_TO_EN_GLOSSARY.keys(), key=lambda k: -len(k)):
        key_norm = unicodedata.normalize('NFKD', key)
        key_norm = ''.join(c for c in key_norm if not unicodedata.combining(c))
        if key_norm in q_norm:
            extras.append(PT_TO_EN_GLOSSARY[key])
    return query + " " + " ".join(extras) if extras else query


def normalize_for_bm25(text: str) -> list[str]:
    """Tokenizer simples lowercase sem acentos para BM25 multilíngue."""
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    return re.findall(r'\b\w+\b', text)


def detect_query_types(query: str) -> set[str]:
    """
    Identifica tipos canônicos mencionados na query.
    Ex.: "pokemon de fogo que voa" → {"fire", "flying"}
    """
    tokens = set(normalize_for_bm25(query))
    found: set[str] = set()
    for type_name, hints in TYPE_HINTS.items():
        hints_norm = set()
        for h in hints:
            hn = unicodedata.normalize("NFKD", h)
            hn = "".join(c for c in hn if not unicodedata.combining(c)).lower()
            hints_norm.add(hn)
        if tokens & hints_norm:
            found.add(type_name)
    return found


class SemanticSearchService:
    """Busca híbrida: FAISS denso + BM25 esparso + RRF + cross-encoder re-ranking."""

    def __init__(self) -> None:
        self._loaded = False
        
    def _load(self):
        if self._loaded:
            return
        
        import pickle
        import numpy as np
        import pandas as pd
        from sentence_transformers import SentenceTransformer, CrossEncoder
        
        data_dir = BASE_DIR / "pokedex_semantic_search"

        # ── Documentos & metadados ──
        with open(data_dir / "documents.json", encoding="utf-8") as f:
            self.documents: list[str] = json.load(f)

        self.metadata: pd.DataFrame = pickle.load(
            open(data_dir / "pokedex_metadata.pkl", "rb")
        )

        # ── Embeddings densos ──
        self.embeddings: np.ndarray = np.load(data_dir / "embeddings.npy", mmap_mode="r")

        # ── Modelo de embedding (E5 multilingual) ──
        self.encoder = SentenceTransformer("intfloat/multilingual-e5-base")

        # ── Índice FAISS ──
        self.faiss_index = None
        try:
            import faiss

            self.faiss_index = faiss.read_index(str(data_dir / "pokedex.index"))
        except Exception:
            pass

        # ── Índice esparso BM25 ──
        self.bm25 = None
        bm25_path = data_dir / "bm25.pkl"
        if bm25_path.exists():
            try:
                with open(bm25_path, "rb") as f:
                    payload = pickle.load(f)
                self.bm25 = payload["bm25"]
            except Exception as e:
                print(f"[WARN] Falha ao carregar BM25: {e}")
        else:
            # fallback: cria BM25 on-the-fly
            try:
                from rank_bm25 import BM25Okapi
                tokens = [normalize_for_bm25(d) for d in self.documents]
                self.bm25 = BM25Okapi(tokens)
            except Exception as e:
                print(f"[WARN] rank-bm25 indisponivel: {e}")


        self.reranker: Optional[CrossEncoder] = None
        if USE_RERANKER:
            try:
                self.reranker = CrossEncoder(RERANKER_MODEL, max_length=512)
                print(f"[OK] Cross-encoder carregado: {RERANKER_MODEL}")
            except Exception as e:
                print(f"[WARN] Re-ranker indisponivel ({e}). Seguindo sem ele.")
        else:
            print("[INFO] Re-ranker desativado (POKEIA_USE_RERANKER!=1).")
        self._loaded = True

    # ─────────────────────────────────────────────────────────────────────
    # Funções auxiliares de retrieval
    # ─────────────────────────────────────────────────────────────────────
    def _dense_search(self, query: str, k: int) -> list[int]:
        import numpy as np
        """Top-k por similaridade densa (FAISS ou numpy)."""
        q_vec = self.encoder.encode(
            [f"query: {query}"], normalize_embeddings=True
        ).astype(np.float32)
        if self.faiss_index is not None:
            _, idx = self.faiss_index.search(q_vec, k)
            return [int(i) for i in idx[0] if i != -1]
        sims = (q_vec @ self.embeddings.T).flatten()
        return list(np.argsort(sims)[::-1][:k].astype(int))

    def _sparse_search(self, query: str, k: int) -> list[int]:
        import numpy as np
        """Top-k por BM25 (lexical). Retorna lista vazia se BM25 indisponível."""
        if self.bm25 is None:
            return []
        tokens = normalize_for_bm25(query)
        scores = self.bm25.get_scores(tokens)
        return list(np.argsort(scores)[::-1][:k].astype(int))

    @staticmethod
    def _reciprocal_rank_fusion(rankings: list[list[int]], k: int = 60) -> dict[int, float]:
        scores: dict[int, float] = {}
        for ranking in rankings:
            for rank, doc_id in enumerate(ranking):
                scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
        return scores

    # ─────────────────────────────────────────────────────────────────────
    # Endpoint principal
    # ─────────────────────────────────────────────────────────────────────
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        self._load()
        """
        Pipeline:
          1) Expande query PT-BR → adiciona tradução EN (para BM25 pegar tipos/conceitos).
          2) Dense (FAISS) top-100  +  Sparse (BM25) top-100.
          3) Funde via Reciprocal Rank Fusion.
          4) Cross-encoder re-rank dos top-50 candidatos.
        """
        # Etapa 1: expansão bilíngue da query
        expanded_query = expand_query_pt_en(query)

        # Etapa 2: dois retrievers em paralelo conceitual
        recall_k = 100
        dense_ids = self._dense_search(expanded_query, recall_k)
        sparse_ids = self._sparse_search(expanded_query, recall_k)

        # Etapa 3: fusão RRF
        if sparse_ids:
            fused = self._reciprocal_rank_fusion([dense_ids, sparse_ids], k=60)
        else:
            fused = {doc_id: 1.0 / (60 + i + 1) for i, doc_id in enumerate(dense_ids)}

        # Etapa 3.5: type-aware boost
        # Se a query menciona tipos (ex: "fogo que voa" → {fire, flying}),
        # damos um bônus proporcional ao número de tipos casados.
        query_types = detect_query_types(query)
        if query_types:
            for doc_id in list(fused.keys()):
                try:
                    poke_types = set(self.metadata.iloc[doc_id]["types"])
                except Exception:
                    continue
                matches = len(query_types & poke_types)
                if matches > 0:
                    # bônus aditivo no score RRF: cada tipo casado adiciona um valor
                    # equivalente a ~rank 1-3 na fusão original
                    fused[doc_id] += 0.05 * matches
                    if matches == len(query_types) and len(query_types) >= 2:
                        # match completo de combo (ex: fire+flying) → bônus extra
                        fused[doc_id] += 0.05

        fused_sorted = sorted(fused.items(), key=lambda x: -x[1])
        rerank_n = max(top_k * 5, 50)
        candidates = [doc_id for doc_id, _ in fused_sorted[:rerank_n]]

        # Etapa 4: re-ranking com cross-encoder
        if self.reranker is not None and len(candidates) > 1:
            pairs = [(query, self.documents[i]) for i in candidates]
            try:
                scores = self.reranker.predict(pairs, show_progress_bar=False)
                ordered = sorted(
                    zip(candidates, scores), key=lambda x: -float(x[1])
                )
                final = ordered[:top_k]
                final_ids = [doc_id for doc_id, _ in final]
                final_scores = [float(s) for _, s in final]
            except Exception as e:
                print(f"[WARN] Re-rank falhou ({e}); usando RRF.")
                final_ids = candidates[:top_k]
                final_scores = [fused[i] for i in final_ids]
        else:
            final_ids = candidates[:top_k]
            final_scores = [fused[i] for i in final_ids]

        results = []
        for idx, score in zip(final_ids, final_scores):
            row = self.metadata.iloc[idx]
            results.append(
                {
                    "id": int(row["id"]),
                    "name": row["name"],
                    "types": str(row["types"]),
                    "sprite": row["sprite"],
                    "is_legendary": bool(row["is_legendary"]),
                    "is_mythical": bool(row["is_mythical"]),
                    "habitat": row.get("habitat"),
                    "generation": int(row["generation"]),
                    "color": row["color"],
                    "score": float(score),
                }
            )
        return results


# ═══════════════════════════════════════════════════
#  2) Team Recommender Service
# ═══════════════════════════════════════════════════
class TeamRecommenderService:
    """Node2Vec embeddings + cosine similarity for teammate recommendations."""

    def __init__(self) -> None:
        self._loaded = False
        
    def _load(self):
        if self._loaded:
            return
            
        import numpy as np
        import pandas as pd
        from gensim.models import Word2Vec
        
        data_dir = BASE_DIR / "team_recommender"

        # Load Node2Vec model
        self.w2v_model = Word2Vec.load(str(data_dir / "node2vec_model.w2v"), mmap="r")

        # Load pre-computed embeddings
        npz = np.load(data_dir / "pokemon_embeddings.npz", allow_pickle=True)
        self.names: np.ndarray = npz["names"]
        self.vectors: np.ndarray = npz["vectors"]

        # Load usage stats
        self.usage_df = pd.read_csv(data_dir / "usage_stats.csv")
        self.usage_map = dict(
            zip(self.usage_df["pokemon"], self.usage_df["usage"])
        )

        # Build name → index lookup
        self.name_to_idx = {n: i for i, n in enumerate(self.names)}
        self._loaded = True

    def recommend(
        self, team: list[str], top_k: int = 5
    ) -> list[dict]:
        self._load()
        import numpy as np
        # Compute team centroid
        valid_vecs = []
        for name in team:
            if name in self.name_to_idx:
                valid_vecs.append(self.vectors[self.name_to_idx[name]])

        if not valid_vecs:
            return []

        centroid = np.mean(valid_vecs, axis=0)
        centroid = centroid / (np.linalg.norm(centroid) + 1e-10)

        # Normalise all vectors
        norms = np.linalg.norm(self.vectors, axis=1, keepdims=True) + 1e-10
        normed = self.vectors / norms

        # Cosine similarities
        sims = normed @ centroid

        # Exclude already-selected Pokémon
        exclude = set(team)
        scored = []
        for i, score in enumerate(sims):
            if self.names[i] not in exclude:
                scored.append((self.names[i], float(score)))

        scored.sort(key=lambda x: x[1], reverse=True)

        results = []
        for name, score in scored[:top_k]:
            results.append(
                {
                    "name": name,
                    "score": score,
                    "usage": self.usage_map.get(name),
                }
            )
        return results

    def get_known_pokemon(self) -> list[str]:
        self._load()
        return list(self.names)


# ═══════════════════════════════════════════════════
#  3) Team Archetype Classifier Service
# ═══════════════════════════════════════════════════
class TeamClassifierService:
    """Logistic Regression classifier for team archetypes."""

    def __init__(self) -> None:
        self._loaded = False
        
    def _load(self):
        if self._loaded:
            return
            
        import joblib
        import numpy as np
        
        data_dir = BASE_DIR / "team_classifier"

        self.model = joblib.load(data_dir / "model.joblib", mmap_mode="r")
        self.scaler = joblib.load(data_dir / "scaler.joblib", mmap_mode="r")
        self.label_encoder = joblib.load(data_dir / "label_encoder.joblib", mmap_mode="r")

        # Load feature names (skip header line "0")
        with open(data_dir / "feature_names.csv") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        # First line is "0" (index header), skip it
        self.feature_names = [l for l in lines if l != "0"]
        self._loaded = True

    def classify(self, features: dict[str, float]) -> dict:
        self._load()
        import numpy as np
        # Build feature vector in the correct order
        vec = np.array(
            [features.get(fn, 0.0) for fn in self.feature_names]
        ).reshape(1, -1)

        # Scale
        vec_scaled = self.scaler.transform(vec)

        # Predict
        pred_idx = self.model.predict(vec_scaled)[0]
        probas = self.model.predict_proba(vec_scaled)[0]

        archetype = self.label_encoder.inverse_transform([pred_idx])[0]
        confidence = float(probas[pred_idx])

        # All class probabilities
        probs = []
        for i, cls in enumerate(self.label_encoder.classes_):
            probs.append({"archetype": cls, "probability": float(probas[i])})

        probs.sort(key=lambda x: x["probability"], reverse=True)

        return {
            "prediction": {"archetype": archetype, "confidence": confidence},
            "probabilities": probs,
        }

    def get_feature_names(self) -> list[str]:
        self._load()
        return self.feature_names

    def get_archetypes(self) -> list[str]:
        self._load()
        return list(self.label_encoder.classes_)

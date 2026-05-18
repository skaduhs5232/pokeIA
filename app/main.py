from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from app.models import (
    SemanticSearchRequest,
    SemanticSearchResponse,
    TeamRecommenderRequest,
    TeamRecommenderResponse,
    TeamClassifierRequest,
    TeamClassifierResponse,
)
from app.services import (
    SemanticSearchService,
    TeamRecommenderService,
    TeamClassifierService,
)

# ── Singletons loaded at startup ──
search_svc: SemanticSearchService | None = None
recommender_svc: TeamRecommenderService | None = None
classifier_svc: TeamClassifierService | None = None


# Load .env from the project root so POKEIA_* settings apply automatically.
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


import threading

@asynccontextmanager
async def lifespan(app: FastAPI):
    global search_svc, recommender_svc, classifier_svc
    
    # Instantiate the services
    search_svc = SemanticSearchService()
    recommender_svc = TeamRecommenderService()
    classifier_svc = TeamClassifierService()
    
    def load_all():
        print("Iniciando carregamento assíncrono (warm-up) dos modelos...")
        try:
            search_svc._load()
            recommender_svc._load()
            classifier_svc._load()
            print("Warm-up concluído com sucesso!")
        except Exception as e:
            print(f"Erro durante o warm-up: {e}")
            
    threading.Thread(target=load_all, daemon=True).start()
    
    yield

    # cleanup (nothing to do)
    print("Encerrando serviço.")


app = FastAPI(
    title="PokeIA API",
    description=(
        "API para consumo dos modelos de IA Pokémon: "
        "Busca Semântica na Pokédex, Recomendação de Times e Classificação de Arquétipos."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
async def health():
    """Verifica se o serviço está ativo e os modelos estão carregados."""
    return {
        "status": "ok",
        "models": {
            "semantic_search": search_svc is not None and getattr(search_svc, "_loaded", False),
            "team_recommender": recommender_svc is not None and getattr(recommender_svc, "_loaded", False),
            "team_classifier": classifier_svc is not None and getattr(classifier_svc, "_loaded", False),
        },
    }

@app.post(
    "/search",
    response_model=SemanticSearchResponse,
    tags=["Pokedex Semantic Search"],
    summary="Busca semântica na Pokédex",
)
async def semantic_search(body: SemanticSearchRequest):
    """
    Recebe um texto em linguagem natural e retorna os Pokémon mais relevantes
    utilizando embeddings (Sentence-Transformers) + FAISS.
    """
    if search_svc is None:
        raise HTTPException(503, "Modelo de busca não carregado.")
    results = search_svc.search(body.query, body.top_k)
    return SemanticSearchResponse(query=body.query, results=results)


@app.post(
    "/recommend",
    response_model=TeamRecommenderResponse,
    tags=["Team Recommender"],
    summary="Recomenda Pokémon para completar o time",
)
async def team_recommend(body: TeamRecommenderRequest):
    """
    Recebe uma lista de Pokémon já selecionados e sugere os melhores parceiros
    utilizando Node2Vec embeddings + similaridade de cosseno.
    """
    if recommender_svc is None:
        raise HTTPException(503, "Modelo de recomendação não carregado.")

    # Validate names
    known = set(recommender_svc.get_known_pokemon())
    unknown = [p for p in body.pokemon if p not in known]
    if unknown:
        raise HTTPException(
            400,
            f"Pokémon não encontrado(s) no modelo: {unknown}. "
            f"Use GET /recommend/pokemon para listar os nomes válidos.",
        )

    recs = recommender_svc.recommend(body.pokemon, body.top_k)
    return TeamRecommenderResponse(
        input_team=body.pokemon, recommendations=recs
    )


@app.get(
    "/recommend/pokemon",
    tags=["Team Recommender"],
    summary="Lista todos os Pokémon conhecidos pelo recomendador",
)
async def list_known_pokemon():
    """Retorna a lista de nomes de Pokémon válidos para o recomendador."""
    if recommender_svc is None:
        raise HTTPException(503, "Modelo de recomendação não carregado.")
    return {"pokemon": recommender_svc.get_known_pokemon()}


@app.post(
    "/classify",
    response_model=TeamClassifierResponse,
    tags=["Team Classifier"],
    summary="Classifica o arquétipo de um time",
)
async def team_classify(body: TeamClassifierRequest):
    """
    Recebe as 64 features agregadas de um time e retorna o arquétipo previsto
    (ex: Hyper Offense, Stall, Balance, etc.) com as probabilidades de cada classe.
    """
    if classifier_svc is None:
        raise HTTPException(503, "Modelo de classificação não carregado.")

    result = classifier_svc.classify(body.features)
    return TeamClassifierResponse(**result)


@app.get(
    "/classify/features",
    tags=["Team Classifier"],
    summary="Lista as features esperadas pelo classificador",
)
async def list_features():
    """Retorna a lista de nomes das 64 features que o classificador espera."""
    if classifier_svc is None:
        raise HTTPException(503, "Modelo de classificação não carregado.")
    return {"features": classifier_svc.get_feature_names()}


@app.get(
    "/classify/archetypes",
    tags=["Team Classifier"],
    summary="Lista os arquétipos possíveis",
)
async def list_archetypes():
    """Retorna a lista de arquétipos que o classificador pode prever."""
    if classifier_svc is None:
        raise HTTPException(503, "Modelo de classificação não carregado.")
    return {"archetypes": classifier_svc.get_archetypes()}

from pydantic import BaseModel, Field
from typing import Optional


# ──────────────────────────────────────────────
# 1) Pokedex Semantic Search
# ──────────────────────────────────────────────
class SemanticSearchRequest(BaseModel):
    query: str = Field(
        ...,
        description="Texto em linguagem natural para buscar Pokémon semanticamente.",
        examples=["pokémon de fogo que voa"],
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Quantidade de resultados a retornar.",
    )


class PokemonResult(BaseModel):
    id: int
    name: str
    types: str
    sprite: str
    is_legendary: bool
    is_mythical: bool
    habitat: Optional[str]
    generation: int
    color: str
    score: float = Field(description="Similaridade (quanto maior, mais relevante).")


class SemanticSearchResponse(BaseModel):
    query: str
    results: list[PokemonResult]


# ──────────────────────────────────────────────
# 2) Team Recommender
# ──────────────────────────────────────────────
class TeamRecommenderRequest(BaseModel):
    pokemon: list[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Lista de 1-5 nomes de Pokémon já escolhidos para o time.",
        examples=[["Koraidon", "Landorus-Therian", "Ferrothorn"]],
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Quantidade de recomendações a retornar.",
    )


class RecommendedPokemon(BaseModel):
    name: str
    score: float = Field(description="Score de compatibilidade (cosseno).")
    usage: Optional[float] = Field(
        default=None,
        description="Taxa de uso competitivo (Smogon).",
    )


class TeamRecommenderResponse(BaseModel):
    input_team: list[str]
    recommendations: list[RecommendedPokemon]


# ──────────────────────────────────────────────
# 3) Team Archetype Classifier
# ──────────────────────────────────────────────
class TeamClassifierRequest(BaseModel):
    features: dict[str, float] = Field(
        ...,
        description=(
            "Dicionário com as 64 features do time. "
            "As chaves são os nomes das features (ex: hp_mean, type_fire, setup_count, etc)."
        ),
        examples=[
            {
                "hp_mean": 80.0,
                "hp_max": 100.0,
                "hp_min": 60.0,
                "hp_std": 15.0,
                "attack_mean": 90.0,
                "attack_max": 130.0,
                "attack_min": 55.0,
                "attack_std": 25.0,
                "defense_mean": 75.0,
                "defense_max": 110.0,
                "defense_min": 50.0,
                "defense_std": 20.0,
                "sp_attack_mean": 85.0,
                "sp_attack_max": 120.0,
                "sp_attack_min": 50.0,
                "sp_attack_std": 22.0,
                "sp_defense_mean": 78.0,
                "sp_defense_max": 105.0,
                "sp_defense_min": 55.0,
                "sp_defense_std": 18.0,
                "speed_mean": 95.0,
                "speed_max": 130.0,
                "speed_min": 60.0,
                "speed_std": 25.0,
                "bst_mean": 503.0,
                "bst_max": 600.0,
                "bst_min": 400.0,
                "bst_std": 65.0,
                "type_normal": 0.0,
                "type_fire": 1.0,
                "type_water": 1.0,
                "type_grass": 0.0,
                "type_electric": 1.0,
                "type_ice": 0.0,
                "type_fighting": 1.0,
                "type_poison": 0.0,
                "type_ground": 1.0,
                "type_flying": 1.0,
                "type_psychic": 0.0,
                "type_bug": 0.0,
                "type_rock": 0.0,
                "type_ghost": 0.0,
                "type_dragon": 1.0,
                "type_dark": 0.0,
                "type_steel": 1.0,
                "type_fairy": 0.0,
                "unique_types": 10.0,
                "has_rain": 0.0,
                "has_sand": 0.0,
                "has_sun": 0.0,
                "has_hail": 0.0,
                "setup_count": 3.0,
                "hazard_count": 1.0,
                "removal_count": 1.0,
                "recovery_count": 1.0,
                "pivot_count": 2.0,
                "status_count": 1.0,
                "off_def_ratio": 1.2,
                "speed_below_60": 0.0,
                "speed_above_100": 4.0,
                "speed_range": 70.0,
                "wall_count": 1.0,
                "stall_ability": 0.0,
                "has_webs": 0.0,
            }
        ],
    )


class ArchetypePrediction(BaseModel):
    archetype: str = Field(description="Classe prevista para o time.")
    confidence: float = Field(description="Confiança da previsão (0-1).")


class ClassifierProbability(BaseModel):
    archetype: str
    probability: float


class TeamClassifierResponse(BaseModel):
    prediction: ArchetypePrediction
    probabilities: list[ClassifierProbability]

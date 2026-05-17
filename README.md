
## 📋 Endpoints

### Health Check

```
GET /health
```

Sem body. Retorna o status do serviço.

**Response:**
```json
{
  "status": "ok",
  "models": {
    "semantic_search": true,
    "team_recommender": true,
    "team_classifier": true
  }
}
```

---

## 1️⃣ Pokedex Semantic Search

### `POST /search`

Busca Pokémon por descrição em linguagem natural utilizando Sentence-Transformers + FAISS.

**Request Body:**
```json
{
  "query": "pokémon de fogo que voa",
  "top_k": 5
}
```

| Campo   | Tipo   | Obrigatório | Descrição                                |
|---------|--------|-------------|------------------------------------------|
| `query` | string | ✅ Sim       | Texto em linguagem natural para buscar   |
| `top_k` | int    | ❌ Não       | Quantidade de resultados (1-50, padrão 5)|

**Response:**
```json
{
  "query": "pokémon de fogo que voa",
  "results": [
    {
      "id": 6,
      "name": "Charizard",
      "types": "['fire', 'flying']",
      "sprite": "https://raw.githubusercontent.com/.../6.png",
      "is_legendary": false,
      "is_mythical": false,
      "habitat": "mountain",
      "generation": 1,
      "color": "red",
      "score": 0.82
    }
  ]
}
```

| Campo          | Tipo    | Descrição                                    |
|----------------|---------|----------------------------------------------|
| `id`           | int     | ID nacional do Pokémon                       |
| `name`         | string  | Nome do Pokémon                              |
| `types`        | string  | Tipos do Pokémon                             |
| `sprite`       | string  | URL do sprite oficial                        |
| `is_legendary` | bool    | Se é lendário                                |
| `is_mythical`  | bool    | Se é mítico                                  |
| `habitat`      | string? | Habitat natural                              |
| `generation`   | int     | Geração de origem                            |
| `color`        | string  | Cor predominante                             |
| `score`        | float   | Score de similaridade (maior = mais relevante)|

---

## 2️⃣ Team Recommender

### `POST /recommend`

Sugere Pokémon para completar um time utilizando Node2Vec embeddings + similaridade de cosseno com dados de uso competitivo (Smogon).

**Request Body:**
```json
{
  "pokemon": ["Koraidon", "Landorus-Therian", "Ferrothorn"],
  "top_k": 5
}
```

| Campo     | Tipo     | Obrigatório | Descrição                                  |
|-----------|----------|-------------|--------------------------------------------|
| `pokemon` | string[] | ✅ Sim       | Lista de 1-5 Pokémon já no time            |
| `top_k`   | int      | ❌ Não       | Quantidade de recomendações (1-20, padrão 5)|

**Response:**
```json
{
  "input_team": ["Koraidon", "Landorus-Therian", "Ferrothorn"],
  "recommendations": [
    {
      "name": "Great Tusk",
      "score": 0.94,
      "usage": 0.329175
    },
    {
      "name": "Dragapult",
      "score": 0.91,
      "usage": 0.261724
    }
  ]
}
```

| Campo   | Tipo   | Descrição                                    |
|---------|--------|----------------------------------------------|
| `name`  | string | Nome do Pokémon recomendado                  |
| `score` | float  | Score de compatibilidade (cosseno, 0 a 1)    |
| `usage` | float? | Taxa de uso competitivo Smogon (pode ser null)|

### `GET /recommend/pokemon`

Lista todos os nomes de Pokémon válidos para o recomendador (482 Pokémon).

**Response:**
```json
{
  "pokemon": ["Great Tusk", "Kingambit", "Gholdengo", "..."]
}
```

---

## 3️⃣ Team Classifier

### `POST /classify`

Classifica o arquétipo de um time a partir de 64 features estatísticas agregadas.

**Arquétipos possíveis:** `Balance`, `Bulky Offense`, `HO Webs`, `Hyper Offense`, `Rain`, `Sand`, `Stall`, `Sun`, `Trick Room`

**Request Body:**
```json
{
  "features": {
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
    "has_webs": 0.0
  }
}
```

**Lista das 64 features esperadas:**

| # | Feature | Descrição |
|---|---------|-----------|
| 1-4 | `hp_mean`, `hp_max`, `hp_min`, `hp_std` | Estatísticas de HP do time |
| 5-8 | `attack_mean`, `attack_max`, `attack_min`, `attack_std` | Estatísticas de Attack |
| 9-12 | `defense_mean`, `defense_max`, `defense_min`, `defense_std` | Estatísticas de Defense |
| 13-16 | `sp_attack_mean`, `sp_attack_max`, `sp_attack_min`, `sp_attack_std` | Estatísticas de Sp. Attack |
| 17-20 | `sp_defense_mean`, `sp_defense_max`, `sp_defense_min`, `sp_defense_std` | Estatísticas de Sp. Defense |
| 21-24 | `speed_mean`, `speed_max`, `speed_min`, `speed_std` | Estatísticas de Speed |
| 25-28 | `bst_mean`, `bst_max`, `bst_min`, `bst_std` | Base Stat Total do time |
| 29-46 | `type_normal` … `type_fairy` | Contagem de cada tipo no time (18 tipos) |
| 47 | `unique_types` | Quantidade de tipos únicos |
| 48-51 | `has_rain`, `has_sand`, `has_sun`, `has_hail` | Presença de setters de clima |
| 52 | `setup_count` | Quantidade de setup sweepers |
| 53 | `hazard_count` | Quantidade de setters de hazard |
| 54 | `removal_count` | Quantidade de removedores de hazard |
| 55 | `recovery_count` | Quantidade com recovery |
| 56 | `pivot_count` | Quantidade de pivots (U-turn, Volt Switch) |
| 57 | `status_count` | Quantidade com moves de status |
| 58 | `off_def_ratio` | Razão ofensiva/defensiva |
| 59 | `speed_below_60` | Pokémon com Speed < 60 |
| 60 | `speed_above_100` | Pokémon com Speed > 100 |
| 61 | `speed_range` | Amplitude de Speed no time |
| 62 | `wall_count` | Quantidade de walls |
| 63 | `stall_ability` | Presença de abilities de stall |
| 64 | `has_webs` | Presença de Sticky Web |

**Response:**
```json
{
  "prediction": {
    "archetype": "Hyper Offense",
    "confidence": 0.87
  },
  "probabilities": [
    { "archetype": "Hyper Offense", "probability": 0.87 },
    { "archetype": "Bulky Offense", "probability": 0.08 },
    { "archetype": "Balance", "probability": 0.03 },
    { "archetype": "HO Webs", "probability": 0.01 },
    { "archetype": "Rain", "probability": 0.005 },
    { "archetype": "Sand", "probability": 0.002 },
    { "archetype": "Sun", "probability": 0.001 },
    { "archetype": "Stall", "probability": 0.001 },
    { "archetype": "Trick Room", "probability": 0.001 }
  ]
}
```

| Campo          | Tipo   | Descrição                                     |
|----------------|--------|-----------------------------------------------|
| `archetype`    | string | Nome do arquétipo previsto                    |
| `confidence`   | float  | Confiança da previsão (0 a 1)                 |
| `probabilities`| array  | Probabilidade de cada arquétipo (ordenado desc)|

### `GET /classify/features`

Lista os nomes das 64 features esperadas pelo classificador.

**Response:**
```json
{
  "features": ["hp_mean", "hp_max", "hp_min", "hp_std", "..."]
}
```

### `GET /classify/archetypes`

Lista os 9 arquétipos possíveis.

**Response:**
```json
{
  "archetypes": ["Balance", "Bulky Offense", "HO Webs", "Hyper Offense", "Rain", "Sand", "Stall", "Sun", "Trick Room"]
}
```

---
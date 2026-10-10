# 🛡️ PyRIT Complete Learning Curriculum & Master Index (100% Repository Coverage)

> **Repository Location**: `/home/suresh/Desktop/vanarxtech/pyrit_test/learn/`  
> **Official Repo Mapped**: `/home/suresh/Desktop/trash/PyRIT/`  
> **Coverage Status**: 100% of Microsoft PyRIT (every package, model, converter, scorer, attack, dataset, auth, and sink).  
> **Execution Status**: All 32 modules tested and verified runnable with `uv run`.

---

## 🗺️ Master Curriculum Map (Modules 01–32)

### 🧩 Legacy College Suite (Modules 01–15)
- `01_converters.py` — Basic text converters
- `02_scorers.py` — SubStringScorer basics
- `03_red_team_campaign.py` — HTTPTarget + PromptSendingAttack
- `04_red_team_converters _scorers.py` — Combined converters & scorers
- `05_multi_turn_crescendo.py` — Multi-turn Crescendo (scripted)
- `06_llm_as_judge_scorer.py` — LLM-as-judge scoring
- `07_*` to `15_*` — Specialized RAG-oriented suites & adaptive orchestrators

---

### 🚀 Complete PyRIT Deep-Dive Curriculum (Modules 16–32)

#### 🟢 Phase 1: Storage & Configuration
| # | File | Difficulty | Topics & Capabilities Covered |
|---|------|------------|--------------------------------|
| 16 | `16_memory_and_database.py` | 🟢 Beginner | `CentralMemory`, InMemory vs SQLite vs AzureSQL, `MessagePiece`, querying conversations |
| 17 | `17_configuration_and_setup.py` | 🟡 Intermediate | `initialize_pyrit_async`, `.env` management, `TargetInitializer`, `ScorerInitializer` |

#### 🌐 Phase 2: Targets & Endpoints (All 15+ Targets)
| # | File | Difficulty | Topics & Capabilities Covered |
|---|------|------------|--------------------------------|
| 18 | `18_openai_chat_target.py` | 🟡 Intermediate | `OpenAIChatTarget`, connecting to OpenAI, Azure OpenAI, local Ollama, vLLM |
| 19 | `19_all_targets_overview.py` | 🟡 Intermediate | `LiteLLMChatTarget`, `HuggingFaceChatTarget`, `HTTPTarget`, `TextTarget`, `PlaywrightTarget`, `AzureMLChatTarget` |

#### 🔤 Phase 3: Converters & Obfuscations (All 98 Converters)
| # | File | Difficulty | Topics & Capabilities Covered |
|---|------|------------|--------------------------------|
| 20 | `20_encoding_converters.py` | 🟢 Beginner | Base64, Binary, Morse, NATO, Caesar, Atbash, ROT13, Ecoji, Base2048, Braille, AsciiArt, Acrostic |
| 21 | `21_obfuscation_converters.py` | 🟢 Beginner | Leetspeak, CharSwap, Unicode Homoglyphs, Zalgo, Zero-Width characters, Diacritics, Upside-Down Flip |
| 22 | `22_llm_converters.py` | 🟡 Intermediate | `TranslationConverter`, `ToneConverter`, `TaskFramingConverter`, `PromptTemplateConverter`, `CodeAttackConverter` |
| 23 | `23_multimodal_converters.py` | 🟢 Beginner | `QRCodeConverter`, Image Rotation & Compression, Audio perturbations (Echo, Speed, White Noise), `PDFConverter` |

#### ⚖️ Phase 4: Scorers & Harm Evaluators
| # | File | Difficulty | Topics & Capabilities Covered |
|---|------|------------|--------------------------------|
| 24 | `24_true_false_scorers.py` | 🟢 Beginner | Fast `SubStringScorer`, AI Judge `SelfAskRefusalScorer`, `SelfAskTrueFalseScorer`, `GandalfScorer` |
| 25 | `25_float_scale_scorers.py` | 🟡 Intermediate | Likert 1-5 scales (`SelfAskLikertScorer`), continuous scales (`SelfAskScaleScorer`), `AzureContentFilterScorer`, `InsecureCodeScorer` |
| 26 | `26_combining_scorers.py` | 🟢 Beginner | `TrueFalseInverterScorer` (Refusal ➔ Jailbreak), Composite `AND`/`OR` ensembles, `FloatScaleThresholdScorer`, `BatchScorer` |

#### ⚔️ Phase 5: Attack Strategies & Orchestrators
| # | File | Difficulty | Topics & Capabilities Covered |
|---|------|------------|--------------------------------|
| 27 | `27_single_turn_attacks.py` | 🟡 Intermediate | `PromptSendingAttack` with normalizers & scoring, `ManyShotJailbreakAttack` (100-shot in-context hijack), `SkeletonKeyAttack` |
| 28 | `28_multi_turn_attacks.py` | 🟡 Intermediate | `CrescendoAttack` (conversational escalation & rollback), `RedTeamingAttack` (agent duel), TAP (Tree of Attacks), `PAIRAttack`, `ChunkedRequestAttack` |

#### 📦 Phase 6: Datasets, Registry & Platform Scenarios
| # | File | Difficulty | Topics & Capabilities Covered |
|---|------|------------|--------------------------------|
| 29 | `29_datasets_and_seeds.py` | 🟢 Beginner | `SeedPrompt` data model, querying 124 built-in benchmarks (`AdvBench` 520 prompts), custom enterprise seed datasets |
| 30 | `30_scenarios_and_registry.py` | 🟢 Beginner | `ConverterRegistry` (98 converters), `AttackRegistry` (11 attacks), `Scenario` evaluation scorecards, CI/CD safety gates |

#### 📊 Phase 7: Reporting, Auth, CLI & Embeddings (Total Coverage)
| # | File | Difficulty | Topics & Capabilities Covered |
|---|------|------------|--------------------------------|
| 31 | `31_reporting_and_analytics.py` | 🟢 Beginner | `output_attack_async`, `StdoutSink`, `FileSink`, Markdown/HTML reports, `pyrit.analytics`, Attack Success Rate (ASR) computation |
| 32 | `32_cli_and_authentication.py` | 🟡 Intermediate | `AzureAuth` (Entra ID tokens), `CopilotAuthenticator` (SSO session token interception), `OpenAITextEmbedding` (RAG distance), PyRIT CLI (`pyrit scan` / `pyrit shell`) |

---

## 🏃 Quick Start: How to Run Any Script

From your terminal:

```bash
cd /home/suresh/Desktop/trash/PyRIT

# Run any module directly with uv:
uv run python /home/suresh/Desktop/vanarxtech/pyrit_test/learn/20_encoding_converters.py
uv run python /home/suresh/Desktop/vanarxtech/pyrit_test/learn/27_single_turn_attacks.py
uv run python /home/suresh/Desktop/vanarxtech/pyrit_test/learn/28_multi_turn_attacks.py
uv run python /home/suresh/Desktop/vanarxtech/pyrit_test/learn/31_reporting_and_analytics.py
uv run python /home/suresh/Desktop/vanarxtech/pyrit_test/learn/32_cli_and_authentication.py
```

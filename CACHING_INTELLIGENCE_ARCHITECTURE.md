# Caching Intelligence - Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Application                           │
└────────────────────┬──────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│         SmartCartographerAgent (Orchestrator)                   │
│                                                                 │
│  - Integrates incremental indexing with intelligence           │
│  - Gets files to analyze                                       │
│  - Runs analysis with predictions                              │
│  - Generates reports                                           │
└────────────────────┬──────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────┐    ┌─────────────────────────────────────┐
│ IncrementalIdx   │    │ CacheIntelligenceManager            │
│                  │    │                                     │
│ - File hashing   │    │ - Orchestrates learning            │
│ - Git tracking   │    │ - Manages cache                    │
│ - Metadata       │    │ - Provides predictions             │
└──────────────────┘    │                                     │
                        │ ┌────────────────────────────────┐ │
                        │ │ GitHistoryAnalyzer             │ │
                        │ │ ├─ find_cochanged_files()      │ │
                        │ │ ├─ analyze_change_frequency()  │ │
                        │ │ └─ find_hot_modules()          │ │
                        │ └────────────────────────────────┘ │
                        │                                     │
                        │ ┌────────────────────────────────┐ │
                        │ │ DependencyGraphBuilder         │ │
                        │ │ ├─ extract_imports()           │ │
                        │ │ ├─ find_dependent_files()      │ │
                        │ │ └─ find_related_files()        │ │
                        │ └────────────────────────────────┘ │
                        │                                     │
                        │ ┌────────────────────────────────┐ │
                        │ │ ChangePrioritizer              │ │
                        │ │ ├─ calculate_change_score()    │ │
                        │ │ ├─ calculate_impact_score()    │ │
                        │ │ └─ prioritize_files()          │ │
                        │ └────────────────────────────────┘ │
                        │                                     │
                        │ ┌────────────────────────────────┐ │
                        │ │ SmartCachePredictor            │ │
                        │ │ ├─ analyze_patterns()          │ │
                        │ │ ├─ predict_needed_analyses()   │ │
                        │ │ ├─ prefetch_related_files()    │ │
                        │ │ └─ get_analysis_plan()         │ │
                        │ └────────────────────────────────┘ │
                        └─────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
        ┌───────────────────────┐       ┌──────────────────────┐
        │   Optimized Files     │       │  Cache Storage       │
        │   (prioritized list)  │       │                      │
        │                       │       │ .cartographer_cache/ │
        │ - Direct changes      │       │ ├─ intelligence.json │
        │ - Dependents          │       │ ├─ metadata.json     │
        │ - Cochanges           │       │ └─ hashes.json       │
        │ - Hotspots            │       │                      │
        └───────────────────────┘       └──────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Fast Analysis        │
        │  (80-95% speedup!)    │
        └───────────────────────┘
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    INITIALIZATION PHASE                         │
│                     (First Run Only)                            │
└─────────────────────────────────────────────────────────────────┘

  All Files
     │
     ├─→ [GitHistoryAnalyzer]
     │   ├─ Analyze commit history
     │   ├─ Find cochange patterns
     │   └─ Calculate frequency
     │
     ├─→ [DependencyGraphBuilder]
     │   ├─ Extract imports
     │   ├─ Build dependency graph
     │   └─ Map relationships
     │
     ├─→ [Repository Learn]
     │   ├─ What breaks together?
     │   ├─ What depends on what?
     │   └─ How often do files change?
     │
     └─→ Save to Cache
         └─ .cartographer_cache/
            ├─ cochange_patterns
            ├─ frequency_data
            ├─ dependency_graph
            └─ last_analyzed

┌─────────────────────────────────────────────────────────────────┐
│                    INCREMENTAL PHASE                            │
│                 (Subsequent Runs - Fast!)                       │
└─────────────────────────────────────────────────────────────────┘

  Files Changed (from git)
     │
     ├─→ [IncrementalIndexer]
     │   └─ Gets only changed files
     │
  Direct Changes ──┐
                  │
                  ├─→ [ChangePrioritizer]
                  │   └─ Calculate scores
                  │
                  ├─→ [SmartCachePredictor] ◄── Load from Cache
                  │   │
                  │   ├─ Dependent files (who imports this?)
                  │   ├─ Cochange files (what breaks together?)
                  │   ├─ Hotspot files (frequently changed?)
                  │   └─ Related files (recursive deps?)
                  │
                  └─→ Analysis Plan
                      ├─ Direct: N files
                      ├─ Predicted: M files (much smaller!)
                      ├─ Priority order
                      └─ Prefetch candidates

  Analysis Plan
     │
     └─→ [cartographer_agent.process_module]
         └─ Analyze only these files!
            (80-95% faster!)
```

## Component Interaction

```
SmartCartographerAgent
├─ initialize()
│  └─ GitHistoryAnalyzer → Analyze git commits
│     DependencyGraphBuilder → Scan imports
│     SmartCachePredictor → Store patterns
│
├─ get_files_to_analyze()
│  ├─ IncrementalIndexer → Get changed files
│  └─ SmartCachePredictor → Predict related files
│
├─ analyze_with_intelligence()
│  ├─ get_files_to_analyze()
│  ├─ process_module() for each file
│  ├─ mark_files_processed()
│  └─ return cypher_queries
│
└─ get_analysis_report()
   └─ Return status of all systems
```

## Decision Tree

```
Is git repo available?
├─ YES
│  └─ Has git history (10+ commits)?
│     ├─ YES
│     │  └─ Cache initialized?
│     │     ├─ NO (first run)
│     │     │  ├─ Analyze all files
│     │     │  ├─ Learn patterns
│     │     │  └─ Save cache
│     │     │
│     │     └─ YES (warm cache)
│     │        ├─ Check: What changed?
│     │        ├─ Predict: What else might break?
│     │        ├─ Prioritize: By importance
│     │        └─ Analyze: Only critical files!
│     │
│     └─ NO (new repo)
│        ├─ Analyze all files
│        └─ Start learning patterns
│
└─ NO (no git)
   └─ Fallback to filename-based caching
      (Still helpful, but less intelligent)
```

## Cache Structure

```
.cartographer_cache/
│
├─ cache_intelligence.json
│  {
│    "cochange_patterns": {
│      "src/core.py": {
│        "src/parser.py": 23,      ← Changed together 23 times
│        "src/lexer.py": 18
│      }
│    },
│    "frequency_data": {
│      "src/core.py": 24,          ← Changed 24 times recently
│      "src/config.py": 15
│    },
│    "dependency_graph": {
│      "src/core.py": ["utils", "config"],
│      "src/main.py": ["core", "utils"]
│    },
│    "last_analyzed": "2025-03-10T14:30:00"
│  }
│
├─ index_metadata.json (from IncrementalIndexer)
│  {
│    "last_indexed": "2025-03-10T14:30:00",
│    "last_commit": "abc123def456...",
│    "total_files_processed": 250
│  }
│
└─ file_hashes.json (from IncrementalIndexer)
   {
     "src/core.py": "abc123def456abc123def456abc123de",
     "src/main.py": "def456abc123def456abc123def456ab"
   }
```

## Performance Model

```
Time Cost = Fixed Overhead + Variable Cost

Fixed Overhead per run:
├─ Load cache: ~100ms
├─ Git history queries: ~200ms
└─ Parse imports: ~500ms (once, then cached)
   Total: ~800ms

Variable Cost per file analyzed:
├─ Read file: ~5ms
├─ Parse code: ~10ms per KB of code
├─ Extract analysis: ~50ms
└─ Generate Cypher: ~10ms
   Total: ~50-200ms per file (depends on size)

Example:
┌────────────────────────────────────────┐
│ Traditional: Analyze all 500 files     │
│ = 800ms + (500 files × 100ms avg)      │
│ = 800ms + 50,000ms                     │
│ = 50.8 seconds ≈ 51 SECONDS            │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ With Intelligence: Analyze 25 files    │
│ = 800ms + (25 files × 100ms avg)       │
│ = 800ms + 2,500ms                      │
│ = 3.3 seconds ≈ 3 SECONDS              │
│                                        │
│ Speedup: 51s / 3s = 17× faster!        │
│ (Even more with parallel workers)      │
└────────────────────────────────────────┘
```

## Learning Feedback Loop

```
Run N:  Analyze files → Generate insights → Update cache
         ↑                                       ↓
         └───────── Learn patterns ─────────────┘

Run N+1: Use learned patterns → Better predictions
         ↑                            ↓
         └── Refine learning ────────┘

Run N+2: Even better predictions
         ↑
         └── Convergence to optimal!
```

## Integration Points

```
┌─────────────────────────────────────┐
│   Existing Code                     │
│   (cartographer_agent.py, etc.)     │
└────────────┬────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ SmartCartographerAgent               │
│ (Thin wrapper with intelligence)     │
└────────┬─────────────────────────────┘
         │ Uses                Uses
         ▼ ↓                   ↓
    ┌─────┘ └─────┬─────────────────────┐
    │             │                     │
    ▼             ▼                     ▼
IncrementalIdx  cartographer_agent  CacheIntelligence
(unchanged)     (unchanged)         (new)

Result: Works with existing code without changes!
```

---

This architecture provides:
- ✅ Intelligent predictions without changing existing code
- ✅ Modular components that can be used independently
- ✅ Persistent learning that improves over time
- ✅ 80-95% performance improvement
- ✅ Zero configuration required

# Component Interaction Diagram

## Translation Chain Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Runner as ExperimentRunner
    participant Chain as TranslationChain
    participant Injector as ErrorInjector
    participant Agent as BaseAgent
    participant Embed as EmbeddingEngine
    participant Distance as DistanceMetrics
    participant Storage as ExperimentStorage

    User->>CLI: run experiment
    CLI->>Runner: execute_experiments()
    
    loop For each sentence
        loop For each error rate
            Runner->>Injector: inject_errors(text, rate)
            Injector-->>Runner: corrupted_text
            
            Runner->>Chain: execute_chain(corrupted_text)
            
            Chain->>Agent: translate(EN→FR)
            Agent-->>Chain: french_text
            
            Chain->>Agent: translate(FR→HE)
            Agent-->>Chain: hebrew_text
            
            Chain->>Agent: translate(HE→EN)
            Agent-->>Chain: english_text
            
            Chain-->>Runner: ChainResult
            
            Runner->>Embed: encode(original_text)
            Embed-->>Runner: original_vector
            
            Runner->>Embed: encode(final_text)
            Embed-->>Runner: final_vector
            
            Runner->>Distance: all_metrics(v1, v2)
            Distance-->>Runner: distances
            
            Runner->>Storage: store_experiment()
            Storage-->>Runner: experiment_id
        end
    end
    
    Runner-->>CLI: completion_status
    CLI-->>User: results summary
```

## Key Interactions

1. **Error Injection**: Controlled corruption of input text
2. **Translation Chain**: Three-stage translation pipeline
3. **Embedding Generation**: Sentence-BERT vector encoding
4. **Distance Calculation**: Cosine, Euclidean, Manhattan metrics
5. **Persistent Storage**: Results saved to SQLite database


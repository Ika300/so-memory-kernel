# SO Memory Kernel SDK

SO Memory Kernelは、コピーしたSpiral Orbit Coreを中心にした軽量な構造記憶SDKです。

LLMでも、ベクトルDBでも、意味検索エンジンでも、要約器でもありません。

自然言語読解ツールではなく、構造化された記憶断片・イベントログ・エージェント履歴・ワークフロー状態・検索trace・関係データを扱うKernelです。

記憶を近似類似度で潰すのではなく、次のような構造として保持します。

- 反復
- 接続
- 緊張
- 空白
- 証拠の独立性
- Patternの同一性
- Return / 再活性化

## 何が違うのか

普通の記憶システムはこう問います。

> 今の入力に似ている過去テキストは何か？

SO Memory Kernelは違います。

> どの構造が反復し、接続し、緊張し、空白を残し、再び活性化しているか？

ここが差別化の核です。

## これは何ではないか

SO Memory Kernelは次のものではありません。

- LLMの代替
- ベクトルDB
- RAGフレームワーク
- 要約AI
- 自然言語パーサー
- 意味辞書

自然言語をどう構造化するかはAdapter側の問題です。Kernel本体は、呼び出し側が渡した構造断片と関係を扱います。

## 使い方

```bash
python examples/simple_memory_demo.py
```

テスト：

```bash
python -m unittest discover -s tests -p '*test*.py' -v
```

用途別example：

```bash
python examples/agent_memory_demo.py
python examples/workflow_memory_demo.py
python examples/rag_trace_memory_demo.py
```

用途ドキュメント：

- [Use cases](docs/use_cases.md)
- [Commercial path](docs/commercial_path.md)

## 最小コード

```python
from so_memory import MemoryFragment, MemoryKernel, MemoryRelation

kernel = MemoryKernel()

result = kernel.run([
    MemoryFragment(
        id="m1",
        content="A memory fragment connects memory and structure.",
        labels=["memory", "structure"],
        relations=[
            MemoryRelation(
                "memory",
                "structure",
                relation_type="bridge",
                strength=0.8,
                directed=False,
            )
        ],
        bridge_potential=0.8,
    )
])
```

## Evidence Identity

区別するもの：

- 独立証拠：誰がその構造を支えたか
- 文脈反復：何回Overlay文脈でその構造が現れたか

これはPatternを減らすための重複排除ではありません。反復は保持します。

## Pattern Identity

Pattern Identityは、Coreが出したPatternの完全一致ベースの構造署名です。

意味が近いから同じ、とは扱いません。

同一とみなす条件：

- Pattern type
- center candidate
- member node order
- edge relation and endpoint signature

## Return / 再活性化

Returnは検索ではありません。

現在の構造が、過去の構造Pattern Identityを再び活性化した候補です。

現在断片は次のように指定します。

```python
MemoryFragment(
    id="current_1",
    content="Current memory.",
    labels=["memory", "structure"],
    metadata={"phase": "current"},
)
```

## 設計制約

Kernelは次を行いません。

- 適当な意味辞書を追加しない
- 近似値マージしない
- 自然言語から勝手にラベルを推測しない
- SOの数式、閾値、Pattern type、Pipeline構造を変更しない
- LLM解釈をCoreに混ぜない

## ベンチマーク

実行：

```bash
python benchmarks/run_benchmarks.py
```

出力：

- `benchmark_results/latest.json`
- `benchmark_results/latest.md`

ベンチ項目：

1. Evidence Identity
2. Pattern Identity
3. Direction Preservation
4. Return / Re-activation
5. No Semantic Guessing
6. Noise Robustness
7. Traceability
8. Agent Memory Trace
9. Workflow Blocker Recurrence
10. RAG Trace Evidence

これはLLM評価ではなく、決定的な構造チェックです。

確認済みスナップショット: [docs/benchmark_snapshot.md](docs/benchmark_snapshot.md)

## ライセンス

Apache-2.0
